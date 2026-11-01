"""Zoomable image view; optionally lets the user click two points."""
import math

from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QPixmap, QPen, QColor, QPainter, QImage
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem


def load_pixmap(path):
    """QPixmap of an image file; falls back to Pillow for formats Qt cannot read."""
    pm = QPixmap(path)
    if not pm.isNull():
        return pm
    from PIL import Image
    im = Image.open(path).convert("RGB")
    data = im.tobytes()
    qi = QImage(data, im.width, im.height, 3 * im.width, QImage.Format_RGB888).copy()
    return QPixmap.fromImage(qi)


class ImageView(QGraphicsView):
    pointsChanged = Signal(list)

    def __init__(self, pick_points=False, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setBackgroundBrush(QColor(40, 40, 40))
        self._item = None
        self._pick = pick_points
        self._points = []
        self._marks = []
        self._pan = None

    def set_image(self, path_or_pixmap):
        sc = self.scene()
        sc.clear()
        self._marks, self._points = [], []
        pm = path_or_pixmap if isinstance(path_or_pixmap, QPixmap) else load_pixmap(path_or_pixmap)
        self._item = QGraphicsPixmapItem(pm)
        sc.addItem(self._item)
        sc.setSceneRect(self._item.boundingRect())
        self.fit()
        self.pointsChanged.emit([])
        return pm

    def clear(self):
        self.scene().clear()
        self._item = None
        self._marks, self._points = [], []

    def fit(self):
        if self._item is not None:
            self.fitInView(self._item, Qt.KeepAspectRatio)

    def wheelEvent(self, e):
        f = 1.25 if e.angleDelta().y() > 0 else 0.8
        self.scale(f, f)

    def mousePressEvent(self, e):
        if e.button() in (Qt.RightButton, Qt.MiddleButton):
            self._pan = e.position()
            self.setCursor(Qt.ClosedHandCursor)
            return
        if self._pick and e.button() == Qt.LeftButton and self._item is not None:
            p = self.mapToScene(e.position().toPoint())
            if len(self._points) >= 2:
                self._points = []
            self._points.append(QPointF(p))
            self._draw_marks()
            self.pointsChanged.emit(list(self._points))
            return
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self._pan is not None:
            d = e.position() - self._pan
            self._pan = e.position()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(d.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(d.y()))
            return
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if self._pan is not None:
            self._pan = None
            self.setCursor(Qt.ArrowCursor)
            return
        super().mouseReleaseEvent(e)

    def _draw_marks(self):
        sc = self.scene()
        for m in self._marks:
            sc.removeItem(m)
        self._marks = []
        pen = QPen(QColor(255, 60, 60))
        pen.setCosmetic(True)
        pen.setWidth(2)
        for p in self._points:
            r = 6
            self._marks.append(sc.addLine(p.x() - r, p.y(), p.x() + r, p.y(), pen))
            self._marks.append(sc.addLine(p.x(), p.y() - r, p.x(), p.y() + r, pen))
        if len(self._points) == 2:
            a, b = self._points
            self._marks.append(sc.addLine(a.x(), a.y(), b.x(), b.y(), pen))

    def distance(self):
        if len(self._points) != 2:
            return None
        a, b = self._points
        return math.hypot(b.x() - a.x(), b.y() - a.y())
