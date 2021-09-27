# -*- coding: utf-8 -*-



from .. import qt_util as qtutil

from .lineplot import LinePlot
from .imgplot import ImagePlot
from .orbitplotter import OrbitPlot
from .threedplot import ThreeDPlot

from PIL.ImageQt import ImageQt
import numpy as np
import os
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5.QtWidgets import QWidget,QTableWidgetItem,QAction,QStyledItemDelegate
from PyQt5.QtCore import Qt,QSize
from PyQt5.QtGui import QColor, QPen, QBrush,QPainter,QColor, QPalette,QPen
import PyQt5
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

DIR = os.path.abspath(os.path.dirname(__file__))
QEarthLightCurveWidget, Ui_EarthLightCurveWidget = uic.loadUiType(os.path.join(DIR, "earthlightcurve.ui"), resource_suffix='') 
from astropy.time import Time
import time
import trimesh
import pyrender
from astropy import units as u
import pyrender
from pyrender.constants import RenderFlags as RenderFlags
from poliastro.bodies import Earth,Mars
from astropy.time import Time
from poliastro.ephem import  Ephem
import math


class CustomThread(QtCore.QThread):
	def __init__(self, target, slotOnFinished=None):
		super(CustomThread, self).__init__()
		self.target = target
		self._args = None
		if slotOnFinished:
			self.finished.connect(slotOnFinished)
	def set_args(self,args):
		self._args = args
	def run(self):
		if self._args:
			self.target(*self._args)
		else:
			self.target()

def length(v):
    return math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2])
def normalize(v):
    l = length(v)
    return [v[0]/l, v[1]/l, v[2]/l] 
def dot(v0, v1):
    return v0[0]*v1[0]+v0[1]*v1[1]+v0[2]*v1[2]
def cross(v0, v1):
    return [
        v0[1]*v1[2]-v1[1]*v0[2],
        v0[2]*v1[0]-v1[2]*v0[0],
        v0[0]*v1[1]-v1[0]*v0[1]]
def m3dLookAt(eye, target, up):
    mz = normalize( (eye[0]-target[0], eye[1]-target[1], eye[2]-target[2]) ) # inverse line of sight
    mx = normalize( cross( up, mz ) )
    my = normalize( cross( mz, mx ) )   

    return np.array([[my[0],mx[0],mz[0],0],[my[1],mx[1],mz[1],0],[my[2],-mx[2],mz[2],0],[0,0,0,1]])
class EarthLightCurveWidget(QEarthLightCurveWidget,Ui_EarthLightCurveWidget):
	def __init__(self,parent):
		QWidget.__init__(self,parent)
		self.setupUi(self)
		self.progressBar.setVisible(False)
		self.progressLabel.setVisible(False)
		
		self._presets = {"Mars": Mars}
		
		self.object = None

		#self.__request_classifiers()
		self.__init_plots()
		self.scene = None
		self.scene =  pyrender.Scene()
		
		
		
		self.cameraNode = None
		self.meshNode = None
		self.sunLightNode = None

		self.r = pyrender.OffscreenRenderer(400, 400)
		self.mesh = None

		#self.loadGPModelThread = CustomThread(self.load_GPModel, self.on_finished_loadingGPModel)
		#self.updateClassThread = CustomThread(self.update_class, self.on_finished_updateClass)
	def clear_scene(self):
		for n in self.sceneNodes:
			try:
				self.scene.remove_node(n)
			except:
				pass

	def __init_plots(self):
		self.orbitplot = OrbitPlot(self.orbitWidget,width = self.lineCurveWidget.width(),
			height=self.lineCurveWidget.height())
		self.orbitLayout.addWidget(self.orbitplot)


		
		
		self.renderedImagePlot = ImagePlot(self.renderedImageWidget,width = self.renderedImageWidget.width(),
			height=self.renderedImageWidget.height())
		self.renderedImageLayout.addWidget(self.renderedImagePlot)
		

		self.lineplot = LinePlot(self.lineCurveWidget,width = self.lineCurveWidget.width(),
			height=self.lineCurveWidget.height())
		self.lineCurveLayout.addWidget(self.lineplot)
		
		return

	def __enable_all_widgets(self,widget):
		for c in widget.findChildren(QWidget):
			c.setEnabled(True)

	def on_pbLoadAsteroid_released(self):
		path = qtutil.browse("openfile")
		if not path:
			return
		meshname = path.split("/")[-1].split(".")[0]
		self.mesh = trimesh.load(path)
		self.lbl_meshName.setText(meshname)
		

	def on_pb_play_released(self):
		if self.mesh is None:
			qtutil.notify("You need to load a mesh first")
			return
		
		sin,cos,rad = np.sin,np.cos,np.deg2rad
		tran = lambda tx,ty,tz: np.array([[1,0,0,tx],[0,1,0,ty],[0,0,1,tz],[0,0,0,1]])
		rot = lambda a,b,g: np.array([[cos(b)*cos(g),cos(b)*sin(g),-sin(b),0],
			[sin(a)*sin(b)*cos(g) - cos(a)*sin(g),sin(a)*sin(b)*sin(g)+cos(a)*cos(g), sin(a)*cos(b),0],
			[cos(a)*sin(b)*cos(g)+sin(a)*sin(g), cos(a)*sin(b)*sin(g)-sin(a)*cos(g),cos(a)*cos(b),0],
			[0,0,0,1]])

		self.sceneNodes = []

		year = int(self.ln_year.text())
		month= int(self.ln_month.text())
		day = int(self.ln_day.text())

		ob = self.cmb_presetOrbit.currentText()
		presetOrbet = self._presets[ob]

		date = Time(f"{year}-{month}-{day}",scale="tdb")

		if self.sunLightNode:
			self.scene.remove_node(self.sunLightNode)

		inten = float(self.ln_lightIntensity.text())
		self.sunLight = pyrender.light.PointLight((1,1,1),inten)
		self.sunLightNode = pyrender.Node(light=self.sunLight,matrix=np.eye(4))
		self.scene.add_node(self.sunLightNode)

		e_t,e_p,b_t,b_p = self.orbitplot.plot(Earth,presetOrbet,date,labels=["Earth",ob],clear=True)
		xe,ye = e_p.get_data()
		xb,yb = b_p.get_data()
		xe,ye,xb,yb = xe[0]/1.496e+6,ye[0]/1.496e+6,xb[0]/1.496e+6,yb[0]/1.496e+6
		# mesh
		if self.meshNode:
			self.scene.remove_node(self.meshNode)
		meshPosX,meshPosY,meshPosZ = xb,yb,0
		meshRotX,meshRotY,meshRotZ = rad(0),rad(0),rad(0)
		meshPose = np.matmul(tran(meshPosX,meshPosY,meshPosZ),
			rot(meshRotX,meshRotY,meshRotZ))
		meshNode = pyrender.Mesh.from_trimesh(self.mesh)
		self.meshNode = pyrender.Node(mesh=meshNode,matrix=meshPose)
		self.scene.add_node(self.meshNode)

		# camera
		if self.cameraNode:
			self.scene.remove_node(self.cameraNode)
		cameraPosX,cameraPosY,cameraPosZ = xe,ye,0
		view_matrix = m3dLookAt([cameraPosX,cameraPosY,cameraPosZ], 
			[meshPosX,meshPosY,meshPosZ], [0, 1, 0])
		dx,dy,dz = cameraPosX-meshPosX,cameraPosY-meshPosY,cameraPosZ-meshPosZ


		cameraPose = np.matmul(tran(cameraPosX,cameraPosY,cameraPosZ),view_matrix)
		cameraYfov,cameraAspectRation = float(self.ln_cameraYfov.text()),float(self.ln_cameraAspectRatio.text())
		camera = pyrender.PerspectiveCamera(yfov=cameraYfov, aspectRatio=cameraAspectRation)
		self.cameraNode = pyrender.Node(camera=camera,matrix=cameraPose)
		self.scene.add_node(self.cameraNode)
		


		period = float(self.ln_period.text())
		dt = float(self.ln_dt.text())
		shotterSpeed = float(self.ln_shutterSpeed.text())
		wX,wY,wZ = float(self.ln_wX.text()),float(self.ln_wY.text()),float(self.ln_wZ.text())
		
		time = 0
		shotTime = 0
		y = []
		currentIntensity = np.zeros((400,400,3))
		line = np.array([0]*int(period/shotterSpeed))
		lineCount = 0
		while time < period:
			time += dt
			shotTime += dt
			meshRotX,meshRotY,meshRotZ = meshRotX+dt*wX,meshRotY+dt*wY,meshRotZ+dt*wZ
			meshPose = np.matmul(tran(meshPosX,meshPosY,meshPosZ),
			rot(rad(meshRotX),rad(meshRotY),rad(meshRotZ)))
			self.scene.set_pose(self.meshNode, pose=meshPose)
			
			color, depth = self.r.render(self.scene)
			RColor = 255-color
			currentIntensity += RColor
			self.renderedImagePlot.plot(RColor,clear=True)
			if shotTime >= shotterSpeed:
				shotTime = 0
				line[lineCount] = currentIntensity.sum()/currentIntensity.size
				self.lineplot.plot(line[:lineCount+1],clear = lineCount == 0)
				lineCount += 1
				currentIntensity = np.zeros((400,400,3))
