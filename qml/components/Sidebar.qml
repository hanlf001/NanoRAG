import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform

Rectangle {
    id: sidebar
    width: 280
    color: "#25262B"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 8

        // Logo
        Text {
            Layout.fillWidth: true
            Layout.topMargin: 6
            text: "NanoRAG"
            color: "white"
            font.pixelSize: 18
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
        }

        // 搜索框
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 36
            color: "#2E2F34"
            radius: 6

            RowLayout {
                anchors.fill: parent
                anchors.margins: 6
                spacing: 6

                Text {
                    text: "🔍"
                    font.pixelSize: 12
                }

                TextInput {
                    id: searchInput
                    Layout.fillWidth: true
                    color: "white"
                    font.pixelSize: 13
                    verticalAlignment: TextInput.AlignVCenter

                    Text {
                        anchors.fill: parent
                        text: "搜索文档..."
                        color: "#6E7179"
                        font.pixelSize: 13
                        verticalAlignment: Text.AlignVCenter
                        visible: !searchInput.text && !searchInput.activeFocus
                    }

                    onTextChanged: {
                        if (nanoRAGBackend) {
                            var results = nanoRAGBackend.searchDocuments(text)
                            console.log("搜索结果:", results.length)
                        }
                    }
                }
            }
        }

        // 对话区域
        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: 4

            Text {
                text: "对话"
                color: "#B5BAC1"
                font.pixelSize: 12
                font.bold: true
            }

            Item { Layout.fillWidth: true }

            Rectangle {
                width: 26
                height: 26
                radius: 4
                color: "#4F8CFF"

                Text {
                    anchors.centerIn: parent
                    text: "+"
                    color: "white"
                    font.pixelSize: 16
                    font.bold: true
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (nanoRAGBackend) nanoRAGBackend.newConversation()
                    }
                }
            }
        }

        ListView {
            id: conversationList
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(160, count * 48 + 4)
            model: nanoRAGBackend ? nanoRAGBackend.conversations : []
            clip: true
            spacing: 4

            delegate: Rectangle {
                width: conversationList.width
                height: 42
                radius: 6
                color: {
                    if (nanoRAGBackend && modelData.id === nanoRAGBackend.currentConversationId)
                        return "#3A3D45"
                    return "transparent"
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (nanoRAGBackend) {
                            nanoRAGBackend.selectConversation(modelData.id)
                        }
                    }
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 8

                    Text {
                        Layout.fillWidth: true
                        text: modelData.title || "新对话"
                        color: "white"
                        font.pixelSize: 13
                        elide: Text.ElideRight
                    }

                    Rectangle {
                        width: 22
                        height: 22
                        radius: 4
                        color: "transparent"
                        z: 10

                        Text {
                            anchors.centerIn: parent
                            text: "🗑"
                            font.pixelSize: 11
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (nanoRAGBackend) {
                                    nanoRAGBackend.deleteConversation(modelData.id)
                                }
                            }
                        }
                    }
                }
            }
        }

        // 分隔线
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: "#3E3F44"
        }

        // 文档区域
        RowLayout {
            Layout.fillWidth: true

            Text {
                text: "文档"
                color: "#B5BAC1"
                font.pixelSize: 12
                font.bold: true
            }

            Item { Layout.fillWidth: true }

            Rectangle {
                width: 26
                height: 26
                radius: 4
                color: "#4F8CFF"

                Text {
                    anchors.centerIn: parent
                    text: "+"
                    color: "white"
                    font.pixelSize: 16
                    font.bold: true
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: fileDialog.open()
                }
            }
        }

        ListView {
            id: documentList
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: nanoRAGBackend ? nanoRAGBackend.documents : []
            clip: true
            spacing: 4

            delegate: Rectangle {
                width: documentList.width
                height: 40
                radius: 6
                color: "#2E2F34"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 8

                    Rectangle {
                        width: 24
                        height: 24
                        radius: 4
                        color: "#4F8CFF"

                        Text {
                            anchors.centerIn: parent
                            text: "📄"
                            font.pixelSize: 11
                        }
                    }

                    Text {
                        Layout.fillWidth: true
                        text: modelData.name
                        color: "white"
                        font.pixelSize: 12
                        elide: Text.ElideRight
                    }

                    Rectangle {
                        width: 22
                        height: 22
                        radius: 4
                        color: "transparent"

                        Text {
                            anchors.centerIn: parent
                            text: "✕"
                            color: "#B5BAC1"
                            font.pixelSize: 12
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (nanoRAGBackend) {
                                    nanoRAGBackend.deleteDocument(modelData.id)
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // Connections for reactive updates
    Connections {
        target: nanoRAGBackend

        function onDocumentListChanged() {
            // model auto-updates via property binding
        }

        function onConversationListChanged() {
            // model auto-updates via property binding
        }
    }

    FileDialog {
        id: fileDialog
        title: "选择文档"
        folder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
        nameFilters: [
            "Documents (*.pdf *.docx *.xlsx *.pptx *.txt *.md)",
            "PDF (*.pdf)",
            "Word (*.docx)",
            "Excel (*.xlsx)",
            "PowerPoint (*.pptx)",
            "Text (*.txt *.md)"
        ]

        onAccepted: {
            if (nanoRAGBackend) {
                nanoRAGBackend.uploadDocument(fileDialog.file)
            }
        }
    }
}
