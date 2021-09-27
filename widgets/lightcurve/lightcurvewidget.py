# -*- coding: utf-8 -*-



from .. import qt_util as qtutil

from .lineplot import LinePlot
from .imgplot import ImagePlot
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
QLightCurveWidget, Ui_LightCurveWidget = uic.loadUiType(os.path.join(DIR, "lightcurvewidget.ui"), resource_suffix='') 
from astropy.time import Time
import time
import trimesh
import pyrender
from astropy import units as u
import pyrender
from pyrender.constants import RenderFlags as RenderFlags

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

class LightCurveWidget(QLightCurveWidget,Ui_LightCurveWidget):
	def __init__(self,parent):
		QWidget.__init__(self,parent)
		self.setupUi(self)
		self.progressBar.setVisible(False)
		self.progressLabel.setVisible(False)
		
		self._presets = {}
		
		self.object = None
		#self.__request_classifiers()
		self.__init_plots()
		self.scene = None
		self.scene =  pyrender.Scene()
		self.sceneNodes = []
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
		self.threeDPlot = ThreeDPlot(self.currentPositionWidget,width = self.lineCurveWidget.width(),
			height=self.lineCurveWidget.height())
		self.positionLayout.addWidget(self.threeDPlot)

		
		
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

		self.clear_scene()
		self.sceneNodes = []

		period = float(self.ln_period.text())
		dt = float(self.ln_dt.text())
		shotterSpeed = float(self.ln_shutterSpeed.text())

		# light
		lightStrength = float(self.ln_lightStrength.text())
		light = pyrender.light.PointLight((1,1,1),lightStrength)
		lightPosX,lightPosY,lightPosZ = float(self.ln_lightX.text()),float(self.ln_lightY.text()),float(self.ln_lightZ.text())
		lightNode = pyrender.Node(light=light,matrix=tran(lightPosX,lightPosY,lightPosZ))
		self.scene.add_node(lightNode)
		self.sceneNodes.append(lightNode)

		# camera
		cameraPosX,cameraPosY,cameraPosZ = float(self.ln_cameraX.text()),float(self.ln_cameraY.text()),float(self.ln_cameraZ.text())
		cameraRX,cameraRY,cameraRZ = rad(float(self.ln_cameraRX.text())),rad(float(self.ln_cameraRY.text())),rad(float(self.ln_cameraRZ.text()))
		cameraPose = np.matmul(tran(cameraPosX,cameraPosY,cameraPosZ),
			rot(cameraRX,cameraRY,cameraRZ))
		cameraYfov,cameraAspectRation = float(self.ln_cameraYfov.text()),float(self.ln_cameraAspectRatio.text())
		camera = pyrender.PerspectiveCamera(yfov=cameraYfov, aspectRatio=cameraAspectRation)
		cameraNode = pyrender.Node(camera=camera,matrix=cameraPose)
		self.sceneNodes.append(cameraNode)
		self.scene.add_node(cameraNode)
		
		# mesh
		meshPosX,meshPosY,meshPosZ = float(self.ln_meshX.text()),float(self.ln_meshY.text()),float(self.ln_meshZ.text())
		meshRotX,meshRotY,meshRotZ = rad(0),rad(0),rad(0)
		meshPose = np.matmul(tran(meshPosX,meshPosY,meshPosZ),
			rot(meshRotX,meshRotY,meshRotZ))
		meshNode = pyrender.Mesh.from_trimesh(self.mesh)
		meshNode = pyrender.Node(mesh=meshNode,matrix=meshPose)
		self.sceneNodes.append(meshNode)
		self.scene.add_node(meshNode)

		# objct anglular velocity
		wX,wY,wZ = float(self.ln_wX.text()),float(self.ln_wY.text()),float(self.ln_wZ.text())
		
		# color, depth = self.r.render(self.scene,)
		# self.renderedImagePlot.plot(color,clear=True)
		self.threeDPlot.plot([lightPosX,cameraPosX,meshPosX],
			[lightPosY,cameraPosY,meshPosY],
			[lightPosZ,cameraPosZ,meshPosZ],
			["*","p","o"],colors=["yellow","blue","red"],
			cameraDir=[cameraRX,cameraRY,cameraRZ],clear=True)


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
			self.scene.set_pose(meshNode, pose=meshPose)
			
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
