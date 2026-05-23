import json
import traceback
import requests
from typing import List, Dict, Optional, Generator, Any
from database.database import NanoRAGDatabase


class LLMEngine:
    def __init__(self, db_path: str = "nano_rag.db", model: str = "qwen3:14b"):
        self.db = NanoRAGDatabase(db_path)
        self.model = model
        self.ollama_url = "http://localhost:11434"
        self.system_prompt = """你是一个有用的AI助手。请基于提供的文档内容回答用户的问题。如果文档中没有相关信息，请诚实地告诉你不知道。"""
        self.ollama_connected = False
        
        self._test_ollama_connection()

    def _test_ollama_connection(self):
        """测试 Ollama 连接"""
        try:
            resp = requests.get(f"{self.ollama_url.rstrip('/')}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                available_models = [m.get('name', '') for m in data.get('models', [])]
                model_found = any(
                    m == self.model or m.startswith(self.model.split(':')[0])
                    for m in available_models
                )
                if model_found:
                    self.ollama_connected = True
                    print(f"Ollama 连接成功 | 模型: {self.model}")
                else:
                    print(f"Ollama 服务运行中，但模型 {self.model} 未找到")
            else:
                print(f"Ollama 服务响应异常 (HTTP {resp.status_code})")
        except requests.ConnectionError:
            print("Ollama 连接失败: 无法连接到服务，请确认 Ollama 已启动")
        except requests.Timeout:
            print("Ollama 连接失败: 连接超时")
        except Exception as e:
            print(f"Ollama 连接失败: {e}")

    def is_available(self) -> bool:
        return self.ollama_connected

    def set_model(self, model: str) -> None:
        self.model = model
        self._test_ollama_connection()

    def set_system_prompt(self, prompt: str) -> None:
        self.system_prompt = prompt

    def _build_prompt(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        context_text = "\n\n".join([
            f"【文档: {doc['document_name']}】\n{doc['content']}"
            for doc in context_docs
        ])
        
        prompt = f"""{self.system_prompt}

请根据以下文档内容回答用户问题：

{context_text}

用户问题：{query}"""
        
        return prompt

    def _build_messages(self, query: str, context_docs: List[Dict[str, Any]], conversation_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": self.system_prompt}]
        
        context_text = "\n\n".join([
            f"【文档: {doc['document_name']}】\n{doc['content']}"
            for doc in context_docs
        ])
        
        if context_text:
            messages.append({
                "role": "user",
                "content": f"请根据以下文档内容回答我的后续问题：\n\n{context_text}"
            })
            messages.append({"role": "assistant", "content": "好的，我会根据提供的文档内容回答您的问题。"})
        
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": query})
        
        return messages

    def chat(self, query: str, context_docs: List[Dict[str, Any]] = None, conversation_id: Optional[int] = None) -> str:
        if not self.is_available():
            return self._fallback_response(query, context_docs)

        conversation_history = []

        if conversation_id:
            messages = self.db.get_messages_by_conversation(conversation_id)
            conversation_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]

        if context_docs is None:
            context_docs = []

        messages = self._build_messages(query, context_docs, conversation_history)

        try:
            url = f"{self.ollama_url.rstrip('/')}/api/chat"
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
            }

            resp = requests.post(url, json=payload, timeout=60)
            resp.raise_for_status()

            data = resp.json()
            return data.get("message", {}).get("content", "")

        except Exception as e:
            error_msg = f"发生错误: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            return self._fallback_response(query, context_docs)

    def chat_stream(self, query: str, context_docs: List[Dict[str, Any]] = None, conversation_id: Optional[int] = None) -> Generator[str, None, None]:
        if not self.is_available():
            yield self._fallback_response(query, context_docs)
            return

        conversation_history = []

        if conversation_id:
            messages = self.db.get_messages_by_conversation(conversation_id)
            conversation_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]

        if context_docs is None:
            context_docs = []

        messages = self._build_messages(query, context_docs, conversation_history)

        try:
            full_answer = ""
            url = f"{self.ollama_url.rstrip('/')}/api/chat"
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": True,
            }

            with requests.post(url, json=payload, timeout=120, stream=True) as resp:
                resp.raise_for_status()

                for line in resp.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if "message" in data and "content" in data["message"]:
                                content = data["message"]["content"]
                                full_answer += content
                                yield content
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            error_msg = f"发生错误: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            yield self._fallback_response(query, context_docs)

    def _fallback_response(self, query: str, context_docs: List[Dict[str, Any]] = None) -> str:
        if not context_docs:
            return """⚠️ 提示：Ollama 未安装或未启动

当前使用【降级模式】
- 文档搜索功能仍可用
- 如需 AI 对话，请安装并启动 Ollama：
  1. 访问 https://ollama.ai 下载安装
  2. 运行命令：ollama pull llama3（或其他模型）
  3. 重启应用"""
        
        result = "📄 找到以下相关文档内容：\n\n"
        for i, doc in enumerate(context_docs, 1):
            content = doc['content']
            if len(content) > 300:
                content = content[:300] + "..."
            result += f"[{i}] {doc['document_name']}:\n{content}\n\n"
        
        result += "\n💡 提示：如需 AI 智能回答，请安装并启动 Ollama"
        return result

    def create_conversation(self, title: str = "新对话") -> int:
        return self.db.create_conversation(title)

    def get_conversation(self, conv_id: int) -> Optional[Dict[str, Any]]:
        conv = self.db.get_conversation(conv_id)
        if conv:
            conv["messages"] = self.db.get_messages_by_conversation(conv_id)
        return conv

    def get_all_conversations(self) -> List[Dict[str, Any]]:
        return self.db.get_all_conversations()

    def delete_conversation(self, conv_id: int) -> bool:
        return self.db.delete_conversation(conv_id)

    def list_models(self) -> List[str]:
        if not self.ollama_connected:
            return []
        
        try:
            resp = requests.get(f"{self.ollama_url.rstrip('/')}/api/tags", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            print(f"获取模型列表失败: {e}")
            return []
