import QtQuick
import QtQuick.Controls

ApplicationWindow {
    visible: true

    width: 1200
    height: 800

    title: "NanoRAG"

    Rectangle {
        anchors.fill: parent
        color: "#1E1F22"

        Text {
            anchors.centerIn: parent

            text: "NanoRAG"

            color: "white"

            font.pixelSize: 32
            font.bold: true
        }
    }
}