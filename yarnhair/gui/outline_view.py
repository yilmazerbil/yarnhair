"""Image view on which the outline of a yarn cross-section is drawn and edited.

Mouse: left click adds a point at the end of the outline; a click close to an
edge inserts a point into that edge; a point can be dragged; right or middle
button moves the image; the wheel zooms. Keys: Backspace removes the last
point, Delete the point under the mouse, Ctrl+Z undoes the last change.
"""
import math

from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainterPath, QPen, QPainter, QKeySequence
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem, QGraphicsPathItem, QGraphicsPixmapItem, \
    QGraphicsScene, QGraphicsView

from .viewer import load_pixmap

HIT = 8           # screen pixels for picking a point
EDGE_HIT = 6      # screen pixels for inserting into an edge


class OutlineView(QGraphicsView):
    outlineChanged = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setBackgroundBrush(QColor(40, 40, 40))
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self._item = None
        self._pts = []
        self._history = []
        self._handles = []
        self._path = None
        self._drag = None          # index of the point being dragged
        self._pan = None
        self.editable = True

    # ---------------------------------------------------------------- image
    def set_image(self, path, points=None):
        sc = self.scene()
        sc.clear()
        self._handles, self._path = [], None
        pm = load_pixmap(path)
        self._item = QGraphicsPixmapItem(pm)
        sc.addItem(self._item)
        sc.setSceneRect(self._item.boundingRect())
        self._pts = [QPointF(float(x), float(y)) for x, y in (points or [])]
        self._history = []
        self.fit()
        self._redraw()
        return pm

    def clear(self):
        self.scene().clear()
        self._item, self._pts, self._handles, self._path, self._history = None, [], [], None, []

    def fit(self):
        if self._item is not None:
            self.fitInView(self._item, Qt.KeepAspectRatio)

    def points(self):
        return [(p.x(), p.y()) for p in self._pts]

    def set_points(self, pts, record=True):
        if record:
            self._push()
        self._pts = [QPointF(float(x), float(y)) for x, y in pts]
        self._redraw()
        self.outlineChanged.emit(self.points())

    def undo(self):
        if self._history:
            self._pts = self._history.pop()
            self._redraw()
            self.outlineChanged.emit(self.points())

    def remove_last(self):
        if self._pts:
            self._push()
            self._pts.pop()
            self._redraw()
            self.outlineChanged.emit(self.points())

    def _push(self):
        self._history.append([QPointF(p) for p in self._pts])
        del self._history[:-200]

    # -------------------------------------------------------------- drawing
    def _redraw(self):
        sc = self.scene()
        for h in self._handles:
            sc.removeItem(h)
        self._handles = []
        if self._path is not None:
            sc.removeItem(self._path)
            self._path = None
        if self._item is None:
            return
        if len(self._pts) >= 2:
            path = QPainterPath(self._pts[0])
            for p in self._pts[1:]:
                path.lineTo(p)
            if len(self._pts) >= 3:
                path.closeSubpath()
            pen = QPen(QColor(255, 220, 0))
            pen.setCosmetic(True)
            pen.setWidth(2)
            self._path = QGraphicsPathItem(path)
            self._path.setPen(pen)
            self._path.setBrush(QBrush(QColor(255, 220, 0, 40)))
            sc.addItem(self._path)
        pen = QPen(QColor(0, 0, 0))
        pen.setCosmetic(True)
        for i, p in enumerate(self._pts):
            h = QGraphicsEllipseItem(QRectF(-4, -4, 8, 8))
            h.setFlag(QGraphicsItem.ItemIgnoresTransformations)
            h.setPos(p)
            h.setPen(pen)
            last = i == len(self._pts) - 1
            h.setBrush(QBrush(QColor(255, 80, 80) if last else QColor(255, 220, 0)))
            sc.addItem(h)
            self._handles.append(h)

    # ---------------------------------------------------------------- mouse
    def _screen(self, p):
        return self.mapFromScene(p)

    def _point_at(self, pos):
        best, bd = None, HIT
        for i, p in enumerate(self._pts):
            q = self._screen(p)
            d = math.hypot(q.x() - pos.x(), q.y() - pos.y())
            if d <= bd:
                best, bd = i, d
        return best

    def _edge_at(self, pos):
        n = len(self._pts)
        if n < 3:
            return None
        best, bd = None, EDGE_HIT
        for i in range(n):
            a, b = self._screen(self._pts[i]), self._screen(self._pts[(i + 1) % n])
            ax, ay, bx, by = a.x(), a.y(), b.x(), b.y()
            L2 = (bx - ax) ** 2 + (by - ay) ** 2
            if L2 == 0:
                continue
            t = ((pos.x() - ax) * (bx - ax) + (pos.y() - ay) * (by - ay)) / L2
            if not 0.05 < t < 0.95:
                continue
            d = math.hypot(ax + t * (bx - ax) - pos.x(), ay + t * (by - ay) - pos.y())
            if d <= bd:
                best, bd = i, d
        return best

    def _inside_image(self, sp):
        r = self._item.boundingRect()
        return QPointF(min(max(sp.x(), 0.0), r.width()), min(max(sp.y(), 0.0), r.height()))

    def wheelEvent(self, e):
        f = 1.25 if e.angleDelta().y() > 0 else 0.8
        self.scale(f, f)

    def mousePressEvent(self, e):
        if e.button() in (Qt.RightButton, Qt.MiddleButton):
            self._pan = e.position()
            self.setCursor(Qt.ClosedHandCursor)
            return
        if e.button() == Qt.LeftButton and self._item is not None and self.editable:
            pos = e.position().toPoint()
            i = self._point_at(pos)
            if i is not None:
                self._push()
                self._drag = i
                return
            sp = self._inside_image(self.mapToScene(pos))
            j = self._edge_at(pos)
            self._push()
            if j is not None:
                self._pts.insert(j + 1, sp)
            else:
                self._pts.append(sp)
            self._redraw()
            self.outlineChanged.emit(self.points())
            return
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self._pan is not None:
            d = e.position() - self._pan
            self._pan = e.position()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(d.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(d.y()))
            return
        if self._drag is not None:
            self._pts[self._drag] = self._inside_image(self.mapToScene(e.position().toPoint()))
            self._redraw()
            return
        if self._item is not None and self.editable:
            pos = e.position().toPoint()
            self.setCursor(Qt.SizeAllCursor if self._point_at(pos) is not None else Qt.CrossCursor)
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if self._pan is not None:
            self._pan = None
            self.setCursor(Qt.ArrowCursor)
            return
        if self._drag is not None:
            self._drag = None
            self.outlineChanged.emit(self.points())
            return
        super().mouseReleaseEvent(e)

    def keyPressEvent(self, e):
        if e.matches(QKeySequence.Undo):
            self.undo()
            return
        if e.key() == Qt.Key_Backspace and self.editable:
            self.remove_last()
            return
        if e.key() == Qt.Key_Delete and self.editable:
            pos = self.mapFromGlobal(self.cursor().pos())
            i = self._point_at(pos)
            if i is not None:
                self._push()
                del self._pts[i]
                self._redraw()
                self.outlineChanged.emit(self.points())
            return
        super().keyPressEvent(e)
