
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout,QTableWidgetItem,QWidget,QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import  pyqtProperty,Qt
DIR = os.path.abspath(os.path.dirname(__file__))


class MeshListItemWidget(QWidget):
    def __init__(self, text, img,objectPath, parent=None):
        QWidget.__init__(self, parent)

        self._text = text
        self._img = img
        self.objectPath = objectPath

        self.setLayout(QVBoxLayout())
        self.lbPixmap = QLabel(self)
        self.lbText = QLabel(self)
        self.lbText.setAlignment(Qt.AlignCenter)
        self.lbPixmap.setAlignment(Qt.AlignCenter)

        self.layout().addWidget(self.lbPixmap)
        self.layout().addWidget(self.lbText)

        self.initUi()

    def initUi(self):
        self.lbPixmap.setPixmap(QPixmap(self._img).scaled(self.lbPixmap.size(),Qt.KeepAspectRatio))
        self.lbText.setText(self._text)


    @pyqtProperty(str)
    def img(self):
        return self._img

    @img.setter
    def total(self, value):
        if self._img == value:
            return
        self._img = value
        self.initUi()

    @pyqtProperty(str)
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if self._text == value:
            return
        self._text = value
        self.initUi()
            