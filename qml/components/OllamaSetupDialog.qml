import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: dialog
    title: "Ollama 安装向导"
    modal: true
    width: 500
    height: 420
    closePolicy: Popup.NoAutoClose

    property int step: 0
    property var recommendedModels: []
    property var selectedModels: []
    property string downloadSpeed: ""
    property bool mirrorEnabled: true
    property string mirrorName: "阿里云"
    property bool modelDownloading: false
    property var downloadedModels: []

    background: Rectangle {
        color: "#1E1F22"
        radius: 12
    }

    Connections {
        target: nanoRAGBackend ? nanoRAGBackend.ollamaManager : null

        function onOllamaDownloadProgress(pct, speed) {
            downloadProgress = pct > 0 ? pct : 0
            downloadSpeed = speed || ""
        }

        function onOllamaDownloadFinished(path) {
            step = 2
        }

        function onOllamaDownloadError(err) {
            downloadError = err
            downloadFailed = true
        }

        function onModelPullProgress(model, pct, speed) {
            for (var i = 0; i < modelList.count; i++) {
                var item = modelList.itemAtIndex(i)
                if (item && item.modelId === model) {
                    item.progress = pct
                    item.speed = speed || ""
                    break
                }
            }
            modelList.model = modelList.model
        }

        function onModelPullFinished(model) {
            downloadedModels.push(model)
            for (var i = 0; i < modelList.count; i++) {
                var item = modelList.itemAtIndex(i)
                if (item && item.modelId === model) {
                    item.progress = 100
                    item.done = true
                    break
                }
            }
            modelList.model = modelList.model
            checkAllDone()
        }

        function onModelPullError(model, err) {
            for (var i = 0; i < modelList.count; i++) {
                var item = modelList.itemAtIndex(i)
                if (item && item.modelId === model) {
                    item.progress = -1
                    item.error = err
                    break
                }
            }
            modelList.model = modelList.model
        }
    }

    property double downloadProgress: 0
    property bool downloadFailed: false
    property string downloadError: ""

    function checkAllDone() {
        var allDone = true
        for (var i = 0; i < modelList.count; i++) {
            var item = modelList.itemAtIndex(i)
            if (item && item.checked && !item.done && item.progress >= 0) {
                allDone = false
                break
            }
        }
        if (allDone && modelDownloading) {
            modelDownloading = false
            step = 4
        }
    }

    // Step 0: Welcome / Not installed
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16
        visible: step === 0

        Text {
            text: "未检测到 Ollama"
            color: "white"
            font.pixelSize: 18
            font.bold: true
        }

        Text {
            text: "NanoRAG 需要 Ollama 才能使用 AI 对话功能。\nOllama 是一个免费的本地 AI 模型运行平台。"
            color: "#B5BAC1"
            font.pixelSize: 13
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: "#3E3F44"
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 50
            color: "#2E2F34"
            radius: 8

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12

                CheckBox {
                    id: mirrorCheck
                    checked: mirrorEnabled
                    onCheckedChanged: mirrorEnabled = checked

                    background: Rectangle { color: "transparent" }
                    indicator: Rectangle {
                        width: 18; height: 18; radius: 4; color: mirrorCheck.checked ? "#4F8CFF" : "#3E3F44"
                        Text { anchors.centerIn: parent; text: "✓"; color: "white"; font.pixelSize: 12; visible: mirrorCheck.checked }
                    }
                }

                Text {
                    text: "下载时自动配置国内镜像源（" + mirrorName + "），加速模型下载"
                    color: "#B5BAC1"
                    font.pixelSize: 12
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Rectangle {
                Layout.fillWidth: true
                height: 40
                radius: 6
                color: "#4F8CFF"

                Text {
                    anchors.centerIn: parent
                    text: "下载并安装 Ollama"
                    color: "white"
                    font.pixelSize: 13
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (mirrorEnabled && nanoRAGBackend && nanoRAGBackend.ollamaManager) {
                            nanoRAGBackend.ollamaManager.configureMirror(mirrorName)
                        }
                        step = 1
                        downloadFailed = false
                        var url = nanoRAGBackend.ollamaManager.getOllamaDownloadUrl()
                        var path = nanoRAGBackend.ollamaManager.getTempDownloadPath()
                        nanoRAGBackend.ollamaManager.startOllamaDownload(url, path)
                    }
                }
            }

            Rectangle {
                width: 80
                height: 40
                radius: 6
                color: "#3E3F44"

                Text {
                    anchors.centerIn: parent
                    text: "跳过"
                    color: "#B5BAC1"
                    font.pixelSize: 13
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: { step = 3; loadRecommendations() }
                }
            }

            Rectangle {
                width: 80
                height: 40
                radius: 6
                color: "#3E3F44"

                Text {
                    anchors.centerIn: parent
                    text: "取消"
                    color: "#E05D5D"
                    font.pixelSize: 13
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: dialog.close()
                }
            }
        }
    }

    // Step 1: Downloading Ollama installer
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16
        visible: step === 1

        Text {
            text: downloadFailed ? "下载失败" : "正在下载 Ollama..."
            color: "white"
            font.pixelSize: 18
            font.bold: true
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 12
            color: "#2E2F34"
            radius: 6

            Rectangle {
                height: parent.height
                width: Math.max(0, parent.width * downloadProgress / 100)
                radius: 6
                color: downloadFailed ? "#E05D5D" : "#4F8CFF"
            }
        }

        Text {
            text: downloadFailed ? downloadError : (downloadProgress.toFixed(0) + "%  " + downloadSpeed)
            color: "#B5BAC1"
            font.pixelSize: 13
            Layout.fillWidth: true
        }

        Text {
            text: "下载失败，请检查网络或尝试手动下载"
            color: "#E05D5D"
            font.pixelSize: 12
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            visible: downloadFailed
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Rectangle {
                Layout.fillWidth: true
                height: 40
                radius: 6
                color: downloadFailed ? "#4F8CFF" : "#3E3F44"
                visible: downloadFailed

                Text {
                    anchors.centerIn: parent
                    text: "重试"
                    color: "white"
                    font.pixelSize: 13
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        downloadFailed = false
                        var url = nanoRAGBackend.ollamaManager.getOllamaDownloadUrl()
                        var path = nanoRAGBackend.ollamaManager.getTempDownloadPath()
                        nanoRAGBackend.ollamaManager.startOllamaDownload(url, path)
                    }
                }
            }

            Rectangle {
                width: 100
                height: 40
                radius: 6
                color: "#3E3F44"

                Text {
                    anchors.centerIn: parent
                    text: "跳过"
                    color: "#B5BAC1"
                    font.pixelSize: 13
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: { step = 3; loadRecommendations() }
                }
            }
        }
    }

    // Step 2: Install Ollama
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16
        visible: step === 2

        Text {
            text: "Ollama 下载完成！"
            color: "white"
            font.pixelSize: 18
            font.bold: true
        }

        Text {
            text: "安装程序已准备就绪。请按照安装向导完成 Ollama 的安装。\n\n安装完成后请点击下方按钮继续。"
            color: "#B5BAC1"
            font.pixelSize: 13
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        Rectangle {
            Layout.fillWidth: true
            height: 40
            radius: 6
            color: "#4F8CFF"

            Text {
                anchors.centerIn: parent
                text: "启动安装程序"
                color: "white"
                font.pixelSize: 13
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    if (nanoRAGBackend && nanoRAGBackend.ollamaManager) {
                        nanoRAGBackend.ollamaManager.installOllama()
                    }
                }
            }
        }

        RowLayout {
            spacing: 12

            Rectangle {
                Layout.fillWidth: true
                height: 40
                radius: 6
                color: "#4F8CFF"

                Text {
                    anchors.centerIn: parent
                    text: "已完成安装，继续"
                    color: "white"
                    font.pixelSize: 13
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: { step = 3; loadRecommendations() }
                }
            }
        }
    }

    // Step 3: Model recommendations
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 12
        visible: step === 3

        Text {
            text: "推荐下载以下模型"
            color: "white"
            font.pixelSize: 18
            font.bold: true
        }

        Text {
            text: "根据你的电脑配置自动推荐。勾选想下载的模型："
            color: "#B5BAC1"
            font.pixelSize: 12
            Layout.fillWidth: true
        }

        ListView {
            id: modelList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 6

            model: ListModel {
                id: listModel
            }

            delegate: Rectangle {
                width: modelList.width
                height: 44
                radius: 6
                color: model.checked ? "#2A3350" : "#2E2F34"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 8

                    CheckBox {
                        checked: model.checked
                        enabled: !model.done && model.progress < 0 ? false : (model.progress <= 0 || model.done)
                        onCheckedChanged: {
                            model.checked = checked
                            selectedModels = []
                            for (var i = 0; i < modelList.count; i++) {
                                var item = modelList.itemAtIndex(i)
                                if (item && item.checked) selectedModels.push(item.modelId)
                            }
                        }

                        background: Rectangle { color: "transparent" }
                        indicator: Rectangle {
                            width: 18; height: 18; radius: 4
                            color: model.done ? "#4CAF50" : (model.progress > 0 && model.progress < 100 ? "#4F8CFF" : (model.checked ? "#4F8CFF" : "#3E3F44"))
                            Rectangle {
                                anchors.centerIn: parent
                                width: 10; height: 10; radius: 2
                                color: model.checked || model.done || (model.progress > 0 && model.progress < 100) ? "white" : "transparent"
                            }
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            text: model.name + (model.recommended ? " ★" : "")
                            color: "white"
                            font.pixelSize: 13
                        }

                        Text {
                            text: model.description + " · " + model.size_gb.toFixed(1) + "GB"
                            color: "#B5BAC1"
                            font.pixelSize: 11
                        }
                    }

                    Text {
                        text: model.done ? "✓ 完成" : (model.progress > 0 ? model.progress.toFixed(0) + "%" : (model.error ? "失败" : ""))
                        color: model.done ? "#4CAF50" : (model.error ? "#E05D5D" : "#B5BAC1")
                        font.pixelSize: 12
                        visible: model.progress > 0 || model.done || !!model.error
                    }
                }

                // Progress bar
                Rectangle {
                    anchors.bottom: parent.bottom
                    width: model.progress > 0 && model.progress < 100 ? parent.width * model.progress / 100 : 0
                    height: 2
                    color: "#4F8CFF"
                    radius: 1
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Rectangle {
                Layout.fillWidth: true
                height: 40
                radius: 6
                color: modelDownloading ? "#3E3F44" : "#4F8CFF"

                Text {
                    anchors.centerIn: parent
                    text: modelDownloading ? "下载中..." : (selectedModels.length > 0 ? "下载选中模型 (" + selectedModels.length + ")" : "开始使用")
                    color: "white"
                    font.pixelSize: 13
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    enabled: !modelDownloading
                    onClicked: {
                        if (selectedModels.length === 0) {
                            dialog.close()
                            return
                        }
                        modelDownloading = true
                        for (var i = 0; i < selectedModels.length; i++) {
                            if (nanoRAGBackend && nanoRAGBackend.ollamaManager) {
                                nanoRAGBackend.ollamaManager.startModelPull(selectedModels[i], mirrorName)
                            }
                        }
                    }
                }
            }

            Rectangle {
                width: 80
                height: 40
                radius: 6
                color: "#3E3F44"

                Text {
                    anchors.centerIn: parent
                    text: "跳过"
                    color: "#B5BAC1"
                    font.pixelSize: 13
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: dialog.close()
                }
            }
        }
    }

    // Step 4: All done
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16
        visible: step === 4

        Text {
            text: "全部完成！"
            color: "white"
            font.pixelSize: 18
            font.bold: true
        }

        Text {
            text: "Ollama 和推荐模型已安装完成。\n\n你可以开始使用 NanoRAG 了。"
            color: "#B5BAC1"
            font.pixelSize: 13
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        Rectangle {
            Layout.fillWidth: true
            height: 40
            radius: 6
            color: "#4F8CFF"

            Text {
                anchors.centerIn: parent
                text: "开始使用"
                color: "white"
                font.pixelSize: 13
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: dialog.close()
            }
        }
    }

    function loadRecommendations() {
        if (nanoRAGBackend && nanoRAGBackend.ollamaManager) {
            var models = nanoRAGBackend.ollamaManager.recommendModels()
            listModel.clear()
            for (var i = 0; i < models.length; i++) {
                var m = models[i]
                listModel.append({
                    modelId: m.id,
                    name: m.name,
                    size_gb: m.size_gb,
                    description: m.description,
                    recommended: m.recommended,
                    checked: m.recommended,
                    progress: 0,
                    done: false,
                    error: "",
                    speed: ""
                })
            }
        }
    }
}
