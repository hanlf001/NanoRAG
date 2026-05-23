import QtQuick
import QtQuick.Controls

Rectangle {
    id: searchBox
    height: 40
    color: "#2E2F34"
    radius: 8
    
    property alias placeholderText: inputField.placeholderText
    signal searchTriggered(string text)
    
    Row {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8
        
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: "🔍"
            font.pixelSize: 14
        }
        
        TextField {
            id: inputField
            Layout.fillWidth: true
            Layout.fillHeight: true
            placeholderText: "搜索文档..."
            color: "white"
            font.pixelSize: 14
            backgroundColor: "transparent"
            selectByMouse: true
            
            onAccepted: searchBox.searchTriggered(text)
        }
    }
}
