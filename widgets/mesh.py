import trimesh
from PyQt5.QtCore import QObject,pyqtSignal
from .config import GALLERY_ITEM_NO_PIC
import os
class Mesh(QObject):
    mesh = None
    signal = pyqtSignal(str,str,str)
    def __init__(self,name,img,path,mesh):
        super().__init__()
        self.name = name
        self.img = img
        self.path = path
        self.mesh = mesh
    
    @classmethod
    def load_mesh(cls,path):
        name = path.split("/")[-1].split(".")[0]
        img = path.replace(".obj",".jpg")
        if not os.path.exists(img):
            img = GALLERY_ITEM_NO_PIC
        mesh = trimesh.load(path)
        if cls.mesh is None:
            cls.mesh = Mesh(name,img,path,mesh)
        else:
            cls.mesh.name = name
            cls.mesh.img = img
            cls.mesh.path = path
            cls.mesh.mesh = mesh
        cls.mesh.signal.emit(name,img,path)


Mesh.mesh = Mesh(None,None,None,None)
        