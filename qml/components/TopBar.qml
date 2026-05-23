import QtQuick
import QtQuick.Controls

Rectangle {
    id: topBar
    height: 50
    color: "#25262B"
    
    property string title: "NanoRAG"
    
    Row {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 16
        
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: topBar.title
            color: "white"
            font.pixelSize: 16
            font.bold: true
        }
        
        Item {
            Layout.fillWidth: true
        }
    }
}
