import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"

ApplicationWindow {
    visible: true
    width: 1200
    height: 800
    minimumWidth: 800
    minimumHeight: 600
    title: "NanoRAG"
    color: "#1E1F22"

    property var messages: []
    property bool isLoading: false
    property bool scrollPending: false

    Component.onCompleted: {
        if (nanoRAGBackend && nanoRAGBackend.conversations.length > 0) {
            var convs = nanoRAGBackend.conversations
            var lastConv = convs[convs.length - 1]
            nanoRAGBackend.selectConversation(lastConv.id)
        }
        checkOllamaLater.start()
    }

    Timer {
        id: checkOllamaLater
        interval: 500
        repeat: false
        onTriggered: {
            if (nanoRAGBackend && nanoRAGBackend.ollamaManager) {
                if (!nanoRAGBackend.ollamaManager.isOllamaInstalled()) {
                    ollamaSetupDialog.open()
                }
            }
        }
    }

    Connections {
        target: nanoRAGBackend

        function onChatResponseChunk(chunk) {
            if (messages.length > 0) {
                var last = messages[messages.length - 1]
                if (last.role === "assistant") {
                    last.content += chunk
                    messages = messages.slice(0, -1).concat(last)
                } else {
                    messages = messages.concat({"role": "assistant", "content": chunk})
                }
            } else {
                messages = [{"role": "assistant", "content": chunk}]
            }
            autoScroll()
        }

        function onChatResponseFinished(text) {
            isLoading = false
            autoScroll()
        }

        function onChatError(text) {
            isLoading = false
            showToast(text)
        }

        function onConversationLoaded(msgList) {
            messages = msgList || []
            isLoading = false
            scrollPending = true
        }

        function onErrorOccurred(text) {
            showToast(text)
        }

        function autoScroll() {
            if (flick.contentHeight > flick.height) {
                var atBottom = flick.contentY + flick.height >= flick.contentHeight - 80
                if (atBottom || isLoading) {
                    flick.contentY = flick.contentHeight - flick.height
                }
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        TopBar {
            Layout.fillWidth: true
            Layout.preferredHeight: 48
            onAboutRequested: aboutDialog.open()
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            Sidebar {
                Layout.preferredWidth: 280
                Layout.fillHeight: true
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#1E1F22"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Flickable {
                        id: flick
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        contentWidth: flick.width
                        contentHeight: msgColumn.implicitHeight + 16
                        clip: true
                        boundsBehavior: Flickable.StopAtBounds

                        onContentHeightChanged: {
                            if (scrollPending) {
                                scrollToBottom()
                                scrollPending = false
                            }
                        }

                        ScrollBar.vertical: ScrollBar {}

                        Column {
                            id: msgColumn
                            width: parent.width
                            spacing: 8

                            Repeater {
                                model: messages

                                Rectangle {
                                    width: Math.min(parent.width - 32, label.implicitWidth + 40)
                                    height: label.height + 24
                                    radius: 12
                                    color: modelData.role === "user" ? "#4F8CFF" : "#2E2F34"
                                    x: modelData.role === "user" ? parent.width - width - 16 : 16

                                    Text {
                                        id: label
                                        anchors.verticalCenter: parent.verticalCenter
                                        anchors.left: parent.left
                                        anchors.leftMargin: 12
                                        text: modelData.content || ""
                                        color: "white"
                                        font.pixelSize: 14
                                        width: Math.min(520, implicitWidth)
                                        wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                                    }
                                }
                            }
                        }

                        function scrollToBottom() {
                            if (contentHeight > height) {
                                contentY = contentHeight - height
                            }
                        }
                    }

                    // 输入区域
                    RowLayout {
                        Layout.fillWidth: true

                        Rectangle {
                            Layout.fillWidth: true
                            height: 44
                            color: "#2E2F34"
                            radius: 8

                            TextInput {
                                id: inputField
                                anchors.fill: parent
                                anchors.margins: 8
                                color: "white"
                                font.pixelSize: 14
                                focus: true

                                Text {
                                    anchors.fill: parent
                                    text: "输入消息..."
                                    color: "#6E7179"
                                    font.pixelSize: 14
                                    verticalAlignment: Text.AlignVCenter
                                    visible: !inputField.text && !inputField.activeFocus
                                }

                                Keys.onReturnPressed: {
                                    if (!isLoading && text.trim()) doSend()
                                }
                            }
                        }

                        Rectangle {
                            width: isLoading ? 80 : 80
                            height: 44
                            radius: 8
                            color: isLoading ? "#E05D5D" : "#4F8CFF"
                            opacity: isLoading ? 1 : (inputField.text.trim() ? 1 : 0.5)

                            Text {
                                anchors.centerIn: parent
                                text: isLoading ? "停止" : "发送"
                                color: "white"
                            }

                            MouseArea {
                                anchors.fill: parent
                                enabled: isLoading || !!inputField.text.trim()
                                onClicked: {
                                    if (isLoading) {
                                        if (nanoRAGBackend) nanoRAGBackend.stopGeneration()
                                        isLoading = false
                                    } else {
                                        doSend()
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // Toast 错误提示
    Rectangle {
        id: toast
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 56
        width: toastLabel.implicitWidth + 40
        height: 40
        radius: 8
        color: "#E05D5D"
        opacity: 0
        z: 100

        Behavior on opacity {
            NumberAnimation { duration: 200 }
        }

        Text {
            id: toastLabel
            anchors.centerIn: parent
            text: ""
            color: "white"
            font.pixelSize: 13
        }

        Timer {
            id: toastTimer
            interval: 3000
            onTriggered: toast.opacity = 0
        }
    }

    function showToast(text) {
        if (!text) return
        toastLabel.text = text
        toast.opacity = 1
        toastTimer.restart()
    }

    function doSend() {
        var text = inputField.text.trim()
        if (!text || isLoading) return
        inputField.text = ""
        isLoading = true
        messages = messages.concat({"role": "user", "content": text})
        Qt.callLater(function() {
            flick.scrollToBottom()
        })
        if (nanoRAGBackend) {
            nanoRAGBackend.sendMessage(text)
        }
    }

    OllamaSetupDialog {
        id: ollamaSetupDialog
    }

    AboutDialog {
        id: aboutDialog
    }
}
