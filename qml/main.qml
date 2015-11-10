import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Dialogs 1.2
import FFD 1.0

ApplicationWindow {
    visible: true
    width: 800
    height: 850

    FileDialog {
        id: fileDialog
        title: "Please choose a file"
        folder: "/home/ac/code/c++/dashi/OBJ/"
        nameFilters: [ "Model files (*.obj)", "All files (*)" ]
        visible: false
        onAccepted: {
            controller.load_file(fileDialog.fileUrls)
        }
    }

    menuBar: MenuBar {
        Menu {
            title: qsTr("File")

            MenuItem {
                text: qsTr("Open file...")
                onTriggered: fileDialog.open()
            }

            MenuItem {
                text: qsTr("Exit")
                onTriggered: Qt.quit();
            }
        }
    }

    Rectangle{
        id:control_panel
        width:200
        anchors.right:parent.right

        Button {
            id: button
            x: 0
            y: 0
            text: qsTr("Button")
            onClicked: {
                controller.test_computer_in_ui_thread()
                console.log("test button pressed")
            }
        }
    }

    Item {
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: control_panel.left
        FFDScene {
            anchors.fill: parent
            objectName: "scene"
        }

        MyMouseArea {
            drag.axis: Drag.XAndYAxis
            anchors.fill: parent
            onRightMoveDelta: {
                controller.move(x, y)
            }
            onLeftMoveInfo: {
                controller.select(x, y, x2, y2)
            }
        }

    }
}


