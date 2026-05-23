import os
import sys
import re
import json
import time
import shutil
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import requests
from PySide6.QtCore import QObject, Signal, Slot, QThread


# ---- Mirror config ----
OLLAMA_MIRRORS = {
    "阿里云": "https://registry.ollama.ai",
    "魔搭社区": "https://ollama.modelscope.cn",
    "浙江大学": "https://ollama.zju.edu.cn",
}

OLLAMA_INSTALLER_URLS = {
    "win32": [
        ("官网", "https://ollama.com/download/OllamaSetup.exe"),
    ],
    "darwin": [
        ("官网", "https://ollama.com/download/Ollama-darwin.zip"),
    ],
}

# ---- Hardware-based model recommendations ----
MODEL_RECOMMENDATIONS = {
    "qwen3:0.6b":     {"name": "Qwen3 0.6B",   "size_gb": 0.5,  "min_ram_gb": 1,  "description": "超轻量，适合低配置"},
    "qwen3:1.7b":     {"name": "Qwen3 1.7B",   "size_gb": 1.2,  "min_ram_gb": 2,  "description": "轻量快速"},
    "qwen3:4b":       {"name": "Qwen3 4B",     "size_gb": 2.8,  "min_ram_gb": 4,  "description": "均衡之选"},
    "qwen3:8b":       {"name": "Qwen3 8B",     "size_gb": 5.5,  "min_ram_gb": 8,  "description": "主流性能"},
    "qwen3:14b":      {"name": "Qwen3 14B",    "size_gb": 9.5,  "min_ram_gb": 16, "description": "高性能"},
    "deepseek-r1:8b": {"name": "DeepSeek R1 8B", "size_gb": 5.5, "min_ram_gb": 8,  "description": "推理能力强"},
}


def get_os_key() -> str:
    if sys.platform.startswith("win"):
        return "win32"
    elif sys.platform == "darwin":
        return "darwin"
    else:
        return "linux"


def get_ollama_path() -> Optional[str]:
    path = shutil.which("ollama")
    if path:
        return path
    if sys.platform.startswith("win"):
        for base in [os.environ.get("LOCALAPPDATA", ""), os.environ.get("PROGRAMFILES", ""), os.environ.get("PROGRAMFILES(X86)", "")]:
            candidate = os.path.join(base, "Ollama", "ollama.exe")
            if os.path.exists(candidate):
                return candidate
    return None


def check_network() -> bool:
    urls = ["https://www.baidu.com", "https://www.aliyun.com", "https://ollama.com"]
    for url in urls:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                return True
        except Exception:
            continue
    return False


def detect_hardware() -> dict:
    info = {
        "ram_gb": 4,
        "cpu_cores": os.cpu_count() or 2,
        "has_gpu": False,
        "os": get_os_key(),
    }
    try:
        import psutil
        info["ram_gb"] = round(psutil.virtual_memory().total / (1024 ** 3), 1)
    except ImportError:
        pass
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            info["has_gpu"] = True
    except Exception:
        pass
    return info


def recommend_models(hardware: dict) -> list:
    ram = hardware["ram_gb"]
    recommended = []
    for model_id, info in MODEL_RECOMMENDATIONS.items():
        if ram >= info["min_ram_gb"]:
            recommended.append({
                "id": model_id,
                "name": info["name"],
                "size_gb": info["size_gb"],
                "description": info["description"],
                "recommended": ram >= info["min_ram_gb"] * 1.5,
            })
    return recommended


def configure_ollama_mirror(mirror_url: str) -> bool:
    try:
        ollama_dir = os.path.join(str(Path.home()), ".ollama")
        os.makedirs(ollama_dir, exist_ok=True)
        config_path = os.path.join(ollama_dir, "config.json")
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        if "registry" not in config:
            config["registry"] = {}
        if "mirrors" not in config["registry"]:
            config["registry"]["mirrors"] = {}
        config["registry"]["mirrors"]["registry.ollama.ai"] = mirror_url
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"配置镜像失败: {e}")
        return False


class DownloadThread(QThread):
    progress = Signal(float, str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, url: str, dest_path: str):
        super().__init__()
        self.url = url
        self.dest_path = dest_path

    def run(self):
        try:
            resp = requests.get(self.url, stream=True, timeout=30)
            resp.raise_for_status()
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0
            start_time = time.time()
            with open(self.dest_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        elapsed = time.time() - start_time
                        speed = ""
                        if elapsed > 0:
                            speed_mb = (downloaded / (1024 * 1024)) / elapsed
                            speed = f"{speed_mb:.1f} MB/s"
                        if total > 0:
                            pct = downloaded / total * 100
                            self.progress.emit(pct, speed)
                        else:
                            self.progress.emit(-1, speed)
            self.finished.emit(self.dest_path)
        except Exception as e:
            self.error.emit(str(e))


class ModelPullThread(QThread):
    progress = Signal(str, float, str)
    finished = Signal(str)
    error = Signal(str, str)

    def __init__(self, model: str, mirror_url: Optional[str] = None):
        super().__init__()
        self.model = model
        self.mirror_url = mirror_url

    def run(self):
        try:
            cmd = ["ollama", "pull", self.model]
            env = os.environ.copy()
            if self.mirror_url:
                env["OLLAMA_REGISTRY_MIRROR"] = self.mirror_url
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, env=env, errors='replace'
            )
            for line in process.stdout:
                line = line.strip()
                match = re.search(r'(\d+)%', line)
                if match:
                    pct = float(match.group(1))
                    speed_match = re.search(r'(\d+\.?\d*\s*(?:MB/s|KB/s|GB/s))', line)
                    speed = speed_match.group(1) if speed_match else ""
                    self.progress.emit(self.model, pct, speed)
            process.wait()
            if process.returncode == 0:
                self.finished.emit(self.model)
            else:
                stderr = process.stderr.read().strip() if process.stderr else ""
                self.error.emit(self.model, stderr or "未知错误")
        except Exception as e:
            self.error.emit(self.model, str(e))


class OllamaManager(QObject):
    ollamaDownloadProgress = Signal(float, str)
    ollamaDownloadFinished = Signal(str)
    ollamaDownloadError = Signal(str)
    modelPullProgress = Signal(str, float, str)
    modelPullFinished = Signal(str)
    modelPullError = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._downloader: Optional[DownloadThread] = None
        self._pullers: List[ModelPullThread] = []

    @Slot(result=bool)
    def isOllamaInstalled(self) -> bool:
        return get_ollama_path() is not None

    @Slot(result=bool)
    def checkNetwork(self) -> bool:
        return check_network()

    @Slot(result=list)
    def detectHardware(self) -> list:
        hw = detect_hardware()
        return [hw["ram_gb"], hw["cpu_cores"], hw["has_gpu"], hw["os"]]

    @Slot(result=list)
    def recommendModels(self) -> list:
        hw = detect_hardware()
        return recommend_models(hw)

    @Slot(str, result=bool)
    def configureMirror(self, mirror_name: str = "阿里云"):
        url = OLLAMA_MIRRORS.get(mirror_name)
        if not url:
            return False
        return configure_ollama_mirror(url)

    @Slot(result=str)
    def getTempDownloadPath(self) -> str:
        ext = ".exe" if sys.platform.startswith("win") else ".zip"
        return os.path.join(tempfile.gettempdir(), f"OllamaSetup{ext}")

    @Slot(str, result=str)
    def getOllamaDownloadUrl(self) -> str:
        os_key = get_os_key()
        urls = OLLAMA_INSTALLER_URLS.get(os_key, [])
        if urls:
            return urls[0][1]
        return ""

    @Slot(str, str, result=bool)
    def startOllamaDownload(self, url: str, save_path: str):
        if self._downloader and self._downloader.isRunning():
            return False
        self._downloader = DownloadThread(url, save_path)
        self._downloader.progress.connect(self.ollamaDownloadProgress)
        self._downloader.finished.connect(self.ollamaDownloadFinished)
        self._downloader.error.connect(self.ollamaDownloadError)
        self._downloader.start()
        return True

    @Slot(result=bool)
    def installOllama(self):
        try:
            path = get_ollama_path()
            if path:
                return True
            if sys.platform.startswith("win"):
                candidates = list(Path.home().glob("Downloads/OllamaSetup*.exe"))
                candidates += list(Path(tempfile.gettempdir()).glob("OllamaSetup*.exe"))
                candidates += list(Path(os.getcwd()).glob("OllamaSetup*.exe"))
                for c in sorted(candidates, key=os.path.getmtime, reverse=True):
                    subprocess.Popen([str(c)], shell=True)
                    return True
        except Exception as e:
            print(f"启动安装程序失败: {e}")
        return False

    @Slot(str, str, result=bool)
    def startModelPull(self, model: str, mirror_name: str = ""):
        mirror_url = OLLAMA_MIRRORS.get(mirror_name, "")
        if not mirror_url:
            mirror_url = OLLAMA_MIRRORS.get("阿里云", "")
        thread = ModelPullThread(model, mirror_url)
        thread.progress.connect(self.modelPullProgress)
        thread.finished.connect(self.modelPullFinished)
        thread.error.connect(self.modelPullError)
        thread.finished.connect(lambda m, t=thread: self._pullers.remove(t) if t in self._pullers else None)
        self._pullers.append(thread)
        thread.start()
        return True

    def cleanup(self):
        if self._downloader and self._downloader.isRunning():
            self._downloader.terminate()
            self._downloader.wait()
        for t in self._pullers:
            if t.isRunning():
                t.terminate()
                t.wait()
        self._pullers.clear()
