import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import Qt.labs.platform

Rectangle {
    id: sidebar
    width: 260
    color: "#25262B"

    Column {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 10

        // Logo区域
        Rectangle {
            width: parent.width
            height: 60
            color: "transparent"

            Text {
                anchors.centerIn: parent
                text: "NanoRAG"
                color: "white"
                font.pixelSize: 20
                font.bold: true
            }
        }

        // 导入按钮
        Rectangle {
            width: parent.width
            height: 40
            radius: 6
            color: "#4F8CFF"

            Text {
                anchors.centerIn: parent
                text: "+ 导入文档"
                color: "white"
                font.pixelSize: 14
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: fileDialog.open()
            }
        }

        // 文档列表标题
        Text {
            text: "文档列表"
            color: "#B5BAC1"
            font.pixelSize: 12
            padding: 6
        }

        // 文档列表
        ListView {
            id: documentList
            width: parent.width
            height: parent.height - 140
            model: nanoRAGBackend ? nanoRAGBackend.documents : []
            clip: true

            delegate: Rectangle {
                width: sidebar.width - 24
                height: 44
                radius: 6
                color: "#2E2F34"
                anchors.horizontalCenter: parent.horizontalCenter

                Row {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 8

                    Rectangle {
                        width: 28
                        height: 28
                        radius: 4
                        color: "#4F8CFF"
                        anchors.verticalCenter: parent.verticalCenter

                        Text {
                            anchors.centerIn: parent
                            text: "📄"
                            font.pixelSize: 14
                        }
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: modelData.name
                        color: "white"
                        font.pixelSize: 13
                        elide: Text.ElideRight
                        width: parent.width - 60
                    }

                    Rectangle {
                        width: 24
                        height: 24
                        radius: 4
                        color: "transparent"
                        anchors.verticalCenter: parent.verticalCenter

                        Text {
                            anchors.centerIn: parent
                            text: "🗑️"
                            font.pixelSize: 12
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                nanoRAGBackend.deleteDocument(modelData.id)
                            }
                        }
                    }
                }
            }

            ScrollIndicator.vertical: ScrollIndicator { }
        }
    }

    FileDialog {
        id: fileDialog
        title: "选择文档"
        folder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
        nameFilters: ["PDF (*.pdf)", "Word (*.docx)", "Excel (*.xlsx)", "PowerPoint (*.pptx)", "Text (*.txt *.md)", "All Files (*)"]

        onAccepted: {
            if (nanoRAGBackend) {
                nanoRAGBackend.uploadDocument(fileDialog.file)
            }
        }
    }
}
