import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: dialog
    title: "关于 NanoRAG"
    modal: true
    width: 420
    height: 350
    parent: ApplicationWindow.overlay

    background: Rectangle {
        color: "#1E1F22"
        radius: 12
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 12

        // Logo 区域
        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            width: 64
            height: 64
            radius: 16
            color: "#4F8CFF"

            Text {
                anchors.centerIn: parent
                text: "NR"
                color: "white"
                font.pixelSize: 22
                font.bold: true
            }
        }

        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "NanoRAG"
            color: "white"
            font.pixelSize: 20
            font.bold: true
        }

        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "v0.1.0"
            color: "#4F8CFF"
            font.pixelSize: 13
        }

        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "轻量级本地 AI 知识库桌面应用"
            color: "#B5BAC1"
            font.pixelSize: 12
        }

        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: "#3E3F44"
        }

        ColumnLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 6

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "北京凡策科技有限公司"
                color: "white"
                font.pixelSize: 13
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "韩丽峰"
                color: "#B5BAC1"
                font.pixelSize: 12
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "18612116621"
                color: "#B5BAC1"
                font.pixelSize: 12
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "hanlf001@163.com"
                color: "#B5BAC1"
                font.pixelSize: 12
            }
        }

        Item { Layout.fillHeight: true }

        Rectangle {
            Layout.fillWidth: true
            height: 36
            radius: 6
            color: "#4F8CFF"

            Text {
                anchors.centerIn: parent
                text: "确定"
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
}
