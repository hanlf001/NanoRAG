import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: topBar
    height: 48
    color: "#25262B"

    property string title: "NanoRAG"
    signal aboutRequested()

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 16

        Text {
            Layout.alignment: Qt.AlignVCenter
            text: topBar.title
            color: "white"
            font.pixelSize: 15
            font.bold: true
        }

        Item { Layout.fillWidth: true }

        Rectangle {
            width: 60
            height: 30
            radius: 6
            color: "transparent"
            Layout.alignment: Qt.AlignVCenter

            Text {
                anchors.centerIn: parent
                text: "关于"
                color: "#B5BAC1"
                font.pixelSize: 12
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: topBar.aboutRequested()
            }
        }

        Text {
            Layout.alignment: Qt.AlignVCenter
            text: "模型:"
            color: "#B5BAC1"
            font.pixelSize: 12
        }

        ComboBox {
            id: modelSelector
            Layout.preferredWidth: 200
            Layout.alignment: Qt.AlignVCenter

            model: nanoRAGBackend ? nanoRAGBackend.modelList : []
            displayText: nanoRAGBackend ? nanoRAGBackend.currentModel : ""

            Component.onCompleted: {
                updateCurrentIndex()
            }

            function updateCurrentIndex() {
                if (!nanoRAGBackend) return
                for (var i = 0; i < model.length; i++) {
                    if (model[i] === nanoRAGBackend.currentModel) {
                        currentIndex = i
                        return
                    }
                }
                currentIndex = -1
            }

            Connections {
                target: nanoRAGBackend
                function onModelChanged() {
                    modelSelector.updateCurrentIndex()
                }
            }

            delegate: ItemDelegate {
                width: modelSelector.width
                contentItem: Text {
                    text: modelData
                    color: "white"
                    font.pixelSize: 13
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: hovered ? "#3E3F44" : "#2E2F34"
                }
            }

            background: Rectangle {
                color: "#2E2F34"
                radius: 6
            }

            contentItem: Text {
                text: modelSelector.displayText
                color: "white"
                font.pixelSize: 13
                verticalAlignment: Text.AlignVCenter
                leftPadding: 8
            }

            onActivated: {
                if (nanoRAGBackend && index >= 0) {
                    nanoRAGBackend.setModel(currentText)
                }
            }

            Popup {
                background: Rectangle {
                    color: "#2E2F34"
                    radius: 6
                }
            }
        }
    }
}
