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
        }

        function onChatResponseFinished(text) {
            isLoading = false
        }

        function onChatError(text) {
            isLoading = false
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Sidebar {
            Layout.preferredWidth: 260
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

                    ScrollBar.vertical: ScrollBar {}

                    Column {
                        id: msgColumn
                        width: parent.width
                        spacing: 8

                        Repeater {
                            model: messages

                            Rectangle {
                                width: Math.min(parent.width - 32, label.width + 40)
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
                                    width: Math.min(360, implicitWidth)
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

                            Keys.onReturnPressed: {
                                if (!isLoading && text.trim()) doSend()
                            }
                        }

                        Text {
                            anchors.fill: parent
                            anchors.margins: 8
                            text: "输入消息..."
                            color: "#6E7179"
                            font.pixelSize: 14
                            visible: !inputField.text && !inputField.activeFocus
                        }
                    }

                    Rectangle {
                        width: 80
                        height: 44
                        radius: 8
                        color: "#4F8CFF"
                        opacity: (!isLoading && inputField.text.trim()) ? 1 : 0.5

                        Text {
                            anchors.centerIn: parent
                            text: "发送"
                            color: "white"
                        }

                        MouseArea {
                            anchors.fill: parent
                            enabled: !isLoading && !!inputField.text.trim()
                            onClicked: doSend()
                        }
                    }
                }
            }
        }
    }

    function doSend() {
        var text = inputField.text.trim()
        if (!text || isLoading) return
        inputField.text = ""
        isLoading = true
        messages = messages.concat({"role": "user", "content": text})
        flick.scrollToBottom()
        if (nanoRAGBackend) {
            nanoRAGBackend.sendMessage(text)
        }
    }
}
