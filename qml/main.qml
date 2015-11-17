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
        anchors.top:parent.top
        anchors.bottom:parent.bottom
        Slider {
            id: slider_x
            y: 512
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.left: parent.left
            anchors.leftMargin: 0
            minimumValue: -1
            onValueChanged: {
                controller.move_control_points(value, 0, 0);
            }
        }

        Slider {
            id: slider_y
            y: 607
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.left: parent.left
            anchors.leftMargin: 0
            minimumValue: -1
            onValueChanged: {
                controller.move_control_points(0, value, 0);
            }
        }

        Slider {
            id: slider_z
            y: 555
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.left: parent.left
            anchors.leftMargin: 0
            minimumValue: -1
            onValueChanged: {
                controller.move_control_points(0, 0, value);
            }
        }
    }

    Item {
        anchors.rightMargin: 15
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: control_panel.left
        FFDScene {
            anchors.fill: parent
            objectName: "scene"
        }

        MyMouseArea {
            anchors.rightMargin: 0
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


