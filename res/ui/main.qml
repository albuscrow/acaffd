import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Dialogs 1.2
import QtQuick.Layouts 1.1
import FFD 1.0

ApplicationWindow {
    visible: true

    FileDialog {
        id: openFileDialog
        folder: "/home/ac/code/python/affd/res/3d_model"
        title: "Please choose a obj file"
        nameFilters: [ "Model files (*.obj)", "All files (*)" ]
        onAccepted: {
                controller.load_file(fileUrls)
        }
    }

    FileDialog {
        id: openControlPointFileDialog
        folder: "/home/ac/code/python/affd/res/3d_model"
        title: "Please choose a npy file"
        nameFilters: [ "Model files (*.npy)", "All files (*)" ]
        onAccepted: {
                controller.load_control_points(fileUrls)
        }
    }


    menuBar: MenuBar {
        Menu {
            title: qsTr("File")

            MenuItem {
                text: qsTr("Open file...")
                onTriggered: {
                    openFileDialog.open()
                }
            }

            MenuItem {
                text: qsTr("Save Ctrl Points...")
                onTriggered: {
                    controller.save_ctrl_points()
                }
            }

            MenuItem {
                text: qsTr("Load Ctrl Points...")
                onTriggered: {
                    openControlPointFileDialog.open()
                }
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
                antialiasing:true
                anchors.fill: parent
                objectName: "scene"
            }

            MyMouseArea {
                anchors.rightMargin: 0
                drag.axis: Drag.XAndYAxis
                anchors.fill: parent
                property int pressKey
                property int modifier
                Keys.onPressed: {
                    pressKey = event.key
                    modifier = event.modifiers
                }
                Keys.onReleased: {
                    pressKey = 0
                }
                Keys.onEscapePressed: {
                    controller.clear_director_control_points()
                }
                onRightMoveDelta: {
                    if (pressKey == Qt.Key_M) {
                        controller.move(x, y)
                    } else {
                        controller.rotate(x, y)
                    }
                }
                onLeftMoveInfo: {
                    controller.left_move(x, y, x2, y2)
                }

                onAcLeftRelease: {
                    controller.cancel_direct_control_point(x, y)
                }

                onWheelMove:{
                    var delta = delta_y / 120;
                    if (key == Qt.Key_X) {
                        if (modifier & Qt.ShiftModifier) {
                            controller.rotate_control_points(delta, 0, 0)
                        } else {
                            controller.move_control_points(delta, 0, 0);
                        }
                    } else if (key == Qt.Key_Y) {
                        if (modifier & Qt.ShiftModifier) {
                            controller.rotate_control_points(0, delta, 0)
                        } else {
                            controller.move_control_points(0, delta, 0);
                        }
                    } else if (key == Qt.Key_Z) {
                        if (modifier & Qt.ShiftModifier) {
                            controller.rotate_control_points(0, 0, delta)
                        } else {
                            controller.move_control_points(0, 0, delta);
                        }
                    } else {
                        controller.zoom(delta)
                    }
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
                    columns: 2
                    anchors.fill: parent

                    Label {
                        text: "切割参数"
                    }

                    SpinBox {
                        value: 0.2
                        decimals: 2
                        stepSize: 0.05
                        onValueChanged: {
                            if (value <= 0) {
                                value = 0.05
                            }
                            controller.change_split_factor(value)
                        }
                    }

                    Label {
                        text: "细分参数"
                    }

                    SpinBox {
                        value: 3
                        onValueChanged: {
                            if (value <= 0) {
                                value = 1
                            }
                            controller.change_tessellation_level(value)
                        }
                    }

                    Label {
                        text: "cp_u"
                    }

                    SpinBox {
                        id: cp_u
                        value: 5
                        onValueChanged: {
                            if (cp_u.value <= 2) {
                                cp_u.value = 3
                            }
                            controller.change_control_point_number(cp_u.value, cp_v.value, cp_w.value)
                        }
                    }

                    Label {
                        text: "cp_v"
                    }

                    SpinBox {
                        id: cp_v
                        value: 5
                        onValueChanged: {
                            if (cp_v.value <= 2) {
                                cp_v.value = 3
                            }
                            controller.change_control_point_number(cp_u.value, cp_v.value, cp_w.value)
                        }
                    }

                    Label {
                        text: "cp_w"
                    }

                    SpinBox {
                        id: cp_w
                        value: 5
                        onValueChanged: {
                            if (cp_w.value <= 2) {
                                cp_w.value = 3
                            }
                            controller.change_control_point_number(cp_u.value, cp_v.value, cp_w.value)
                        }
                    }

                    Label {
                        text: "order"
                    }

                    SpinBox {
                        id: order
                        value: 3
                        onValueChanged: {
                            if (cp_w.value <= 2) {
                                cp_w.value = 3
                            }
                            controller.change_control_point_order(value)
                        }
                    }

                    CheckBox {
                        text: qsTr("显示控制定点")
                        checked: false
                        onClicked: {
                            controller.set_control_point_visibility(checked)
                        }
                    }
                    //?!iftime
                    //?!else
                    CheckBox {
                        text: qsTr("显示切割边界")
                        checked: false
                        onClicked: {
                            controller.set_splited_edge_visibility(checked)
                        }
                    }

                    CheckBox {
                        text: qsTr("显示三角形质量")
                        checked: false
                        onClicked: {
                            controller.set_show_triangle_quality_flag(checked)
                        }
                    }

                    CheckBox {
                        text: qsTr("显示控制顶点")
                        checked: false
                        onClicked: {
                            controller.set_show_control_point(checked)
                        }
                    }

                    CheckBox {
                        text: qsTr("显示法向差异")
                        checked: false
                        onClicked: {
                            controller.set_show_normal_diff_flag(checked)
                        }
                    }
                    CheckBox {
                        text: qsTr("显示位置差异")
                        checked: false
                        onClicked: {
                            controller.set_show_position_diff_flag(checked)
                        }
                    }
                    CheckBox {
                        text: qsTr("显示PN法向")
                        checked: false
                        onClicked: {
                            controller.set_show_normal(checked)
                        }
                    }
                    CheckBox {
                        text: qsTr("调整控制定点")
                        checked: true
                        onClicked: {
                            controller.set_adjust_control_point(checked)
                        }
                    }
                    CheckBox {
                        text: qsTr("显示原始模型")
                        checked: false
                        onClicked: {
                            controller.set_show_original(checked)
                        }
                    }
                    CheckBox {
                        text: qsTr("显示上采样直接变形结果")
                        checked: false
                        onClicked: {
                            controller.set_show_real(checked)
                        }
                    }
                    Button {
                        text: "打印精度对比"
                        onClicked: {
                            controller.begin_diff_comparison()
                        }
                    }

                    Button {
                        text: "测试分割尺度"
                        onClicked: {
                            controller.begin_test_split_factor()
                        }
                    }
                    //?!end

                    ExclusiveGroup { id: group }
                    RadioButton {
                        text: "ac"
                        exclusiveGroup: group
                        checked: true
                        onClicked: {
                            controller.change_algorithm(0)
                        }
                    }
                    RadioButton {
                        text: "cym"
                        exclusiveGroup: group
                        onClicked: {
                            controller.change_algorithm(1)
                        }
                    }

                    CheckBox {
                        text: qsTr("pn法向绘制")
                        checked: false
                        onClicked: {
                            controller.set_use_pn_normal(checked)
                        }
                    }
                }
            }
        }
    }
}
