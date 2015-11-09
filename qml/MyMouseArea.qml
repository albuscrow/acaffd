import QtQuick 2.5

MouseArea {
    property point origin
    property point last
    property bool ready: false
    property int threshold: 10
    signal move(int x, int y)
    signal swipe(string direction)

    onPressed: {
        drag.axis = Drag.XAndYAxis
        origin = Qt.point(mouse.x, mouse.y)
        last = Qt.point(mouse.x, mouse.y)
    }

    onPositionChanged: {
        switch (drag.axis) {
        case Drag.XAndYAxis:
//            if (Math.abs(mouse.x - origin.x) > threshold ) {
//                drag.axis = Drag.XAxis
//            }
//            else if (Math.abs(mouse.y - origin.y) > threshold) {
//                drag.axis = Drag.YAxis
//            }
            move(mouse.x - last.x, mouse.y - last.y)
            break
        case Drag.XAxis:
            move(mouse.x - last.x, 0)
            break
        case Drag.YAxis:
            move(0, mouse.y - last.y)
            break
        }
        last = Qt.point(mouse.x, mouse.y)
    }

    onReleased: {
        switch (drag.axis) {
        case Drag.XAndYAxis:
            canceled(mouse)
            break
        case Drag.XAxis:
            swipe(mouse.x - origin.x < 0 ? "left" : "right")
            break
        case Drag.YAxis:
            swipe(mouse.y - origin.y < 0 ? "up" : "down")
            break
        }
    }
}

