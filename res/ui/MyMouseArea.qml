import QtQuick 2.5

MouseArea {
    property point origin
    property point last
    property int threshold: 10
    signal rightMoveDelta(int x, int y)
    signal leftMoveInfo(int x, int y, int x2, int y2)
    signal wheelMove(int key, int delta_y)
    acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton

    onPressed: {
        focus = true
        origin = Qt.point(mouse.x, mouse.y)
        last = Qt.point(mouse.x, mouse.y)
        if (mouse.modifiers & Qt.ShiftModifier) {
            drag.axis = Drag.XAxis
        } else if (mouse.modifiers & Qt.AltModifier) {
            drag.axis = Drag.YAxis
        } else {
            drag.axis = Drag.XAndYAxis
        }
        if (mouse.button == Qt.LeftButton) {
            leftMoveInfo(origin.x, origin.y, mouse.x, mouse.y)
        }
    }

    onPositionChanged: {
        switch (drag.axis) {
        case Drag.XAndYAxis:
            if (pressedButtons & Qt.RightButton){
                rightMoveDelta(mouse.x - last.x, mouse.y - last.y)
            } else {
                leftMoveInfo(origin.x, origin.y, mouse.x, mouse.y)
            }
            break
        case Drag.XAxis:
            if (pressedButtons & Qt.RightButton){
                rightMoveDelta(mouse.x - last.x, 0)
            }
            break
        case Drag.YAxis:
            if (pressedButtons & Qt.RightButton){
                rightMoveDelta(0, mouse.y - last.y)
            }
            break
        }
        last = Qt.point(mouse.x, mouse.y)
    }
    focus: true

    property int pressedKey
    Keys.onPressed: {
        pressedKey = event.key
    }

    Keys.onReleased: {
        pressedKey = -1
    }
    onWheel: {
        wheelMove(pressedKey, wheel.angleDelta.y)
    }
}

