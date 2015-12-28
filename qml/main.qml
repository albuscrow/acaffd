import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Dialogs 1.2
import QtQuick.Layouts 1.1
import FFD 1.0

ApplicationWindow {
    visible: true

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

    SplitView {
        id: mainLayout
        anchors.fill: parent
        orientation: Qt.Horizontal;

        Item {
            Layout.fillWidth: true;
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

        ColumnLayout {
            id:control_panel
            width:300
            GroupBox {
                id: parameter_panel
                title: "参数调整"
                Layout.fillWidth: true

                GridLayout {
                    columns: 4
                    anchors.fill: parent
                    Label {
                        text: "切割参数"
                    }

                    SpinBox {
                        id: split_param_spin_box
                        value: 3
                        onValueChanged: {
                            controller.change_tessellation_level(value)
                        }
                    }

                    Label {
                        text: "细分参数"
                    }

                    SpinBox {
                        id: tessellation_param_spin_box
                    }

                    Label {
                        text: "切割参数"
                    }

                    SpinBox {
                    }

                    Label {
                        text: "细分参数"
                    }

                    SpinBox {
                    }

                    Label {
                        text: "切割参数"
                    }

                    SpinBox {
                    }

                    Label {
                        text: "细分参数"
                    }

                    SpinBox {
                    }

                    Label {
                        text: "切割参数"
                    }

                    SpinBox {
                    }

                    Label {
                        text: "细分参数"
                    }

                    SpinBox {
                    }
                }
            }

            GroupBox {
                id: edit_panel
                title: "编辑"
                Layout.fillWidth: true

                GridLayout {
                    anchors.fill: parent
                    columns: 2

                    Label {
                        text: "切割参数"
                    }
                    Slider {
                        id: slider_x
                        Layout.fillWidth: true
                        minimumValue: -1
                        onValueChanged: {
                            controller.move_control_points(value, 0, 0);
                        }
                    }

                    Label {
                        text: "切割参数"
                    }

                    Slider {
                        Layout.fillWidth: true
                        id: slider_y
                        minimumValue: -1
                        onValueChanged: {
                            controller.move_control_points(0, value, 0);
                        }
                    }

                    Label {
                        text: "切割参数"
                    }

                    Slider {
                        Layout.fillWidth: true
                        id: slider_z
                        minimumValue: -1
                        onValueChanged: {
                            controller.move_control_points(0, 0, value);
                        }
                    }
                }
            }
        }
    }
}


