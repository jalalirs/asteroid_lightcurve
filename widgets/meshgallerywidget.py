

import os
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt


import glob
from .meshlistitemwidget import MeshListItemWidget
from .qt_util import notify
from .mesh import Mesh

DIR = os.path.abspath(os.path.dirname(__file__))
QMeshGalleryWidget, Ui_MeshGalleryWidget = uic.loadUiType(os.path.join(DIR, "meshgallerywidget.ui"), resource_suffix='') 


class MeshGalleryWidget(QMeshGalleryWidget, Ui_MeshGalleryWidget):
    def __init__(self,path,nopic=None,parent=None):
        super(MeshGalleryWidget,self).__init__(parent)
        self.setupUi(self)
        self.path = path
        self.cellWidgets = []
        self.nopic = nopic
        self._load()
        self.tbl_gallery.resizeColumnsToContents()
        self.tbl_gallery.resizeRowsToContents()
        header = self.tbl_gallery.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.tbl_gallery.cellClicked.connect(self.cell_was_clicked)
        self.row = None
        self.col = None
        
    
    def _load(self):
        objs = glob.glob(f"{self.path}/*.obj")
        ncols = 4
        for i,o in enumerate(objs):
            itemname = o.split("/")[-1].split(".")[0]
            itemimage = o.replace(".obj",".jpg")
            
            if not os.path.exists(itemimage):
                itemimage = self.nopic
            item = MeshListItemWidget(itemname,itemimage,o)
            if i%ncols == 0:
                self.tbl_gallery.insertRow(i/ncols)
                self.cellWidgets.append([])
            self.cellWidgets[-1].append(item)
            self.tbl_gallery.setCellWidget(i/ncols,i%ncols,item)
        if len(objs) % ncols > 0:
            offsetItems = len(objs) % ncols
            row = int(len(objs)/ncols)
            for i in range(offsetItems,ncols):
                self.tbl_gallery.setItem(row,i,QTableWidgetItem())
                self.tbl_gallery.item(row,i).setFlags(Qt.NoItemFlags)
    def cell_was_clicked(self,row, column):
        self.row = row
        self.column = column
    def on_pb_load_released(self):
    
        if self.row is None:
            notify("Please select a mesh first")
            return
        item = self.cellWidgets[self.row][self.column]
        path = item.objectPath
        Mesh.load_mesh(path)
        notify("Mesh is loaded","info")
    
            