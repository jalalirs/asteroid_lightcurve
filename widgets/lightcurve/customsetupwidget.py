# -*- coding: utf-8 -*-



from .. import qt_util as qtutil
from .lineplot import LinePlot
from .imgplot import ImagePlot
from .threedplot import ThreeDPlot
from ..mesh import Mesh

import numpy as np
import os
from astropy.time import Time
import time
import trimesh
import pyrender
from astropy import units as u
import pyrender
from pyrender.constants import RenderFlags as RenderFlags

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QIcon, QPixmap

DIR = os.path.abspath(os.path.dirname(__file__))
QCustomSetupWidget, Ui_CustomSetupWidget = uic.loadUiType(os.path.join(DIR, "customsetupwidget2.ui"), resource_suffix='') 




class CustomSetupWidget(QCustomSetupWidget,Ui_CustomSetupWidget):
	def __init__(self,parent):
		QWidget.__init__(self,parent)
		self.setupUi(self)
		
		self._presets = {}
		
		self.object = None
		self.__init_plots()
		self.scene = None
		self.scene =  pyrender.Scene()
		self.sceneNodes = []
		self.r = pyrender.OffscreenRenderer(400, 400)
		self.mesh = None
		Mesh.mesh.signal.connect(self.onMeshChanged)
	
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
		Mesh.load_mesh(path)
		self.lbl_meshName.setText(meshname)
		
	def on_pb_stop_released(self):
		self.play= False
	def on_pb_play_released(self):
		if self.mesh is None:
			qtutil.notify("You need to load a mesh first")
			return
		self.pb_play.setEnabled(False)
		self.pb_stop.setEnabled(True)
		self.play = True
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
		lightType = self.cmb_lightType.currentText()
		if lightType == "Point":
			light = pyrender.light.PointLight((1,1,1),lightStrength)
		elif lightType == "Directional":
			light = pyrender.light.DirectionalLight((1,1,1),lightStrength)
		elif lightType == "Spot":
			light = pyrender.light.SpotLight((1,1,1),lightStrength)
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
		currentIntensity = 0
		line = np.array([0]*int(period/shotterSpeed))
		lineCount = 0
		while time < period and self.play:
			time += dt
			shotTime += dt
			meshRotX,meshRotY,meshRotZ = meshRotX+dt*wX,meshRotY+dt*wY,meshRotZ+dt*wZ
			meshPose = np.matmul(tran(meshPosX,meshPosY,meshPosZ),
			rot(rad(meshRotX),rad(meshRotY),rad(meshRotZ)))
			self.scene.set_pose(meshNode, pose=meshPose)
			
			color, depth = self.r.render(self.scene)
			color = color.copy()
			color[depth == 0] = 0
			currentIntensity += color.sum()
			self.renderedImagePlot.plot(color,clear=True)
			if shotTime >= shotterSpeed:
				shotTime = 0
				line[lineCount] = currentIntensity#currentIntensity.sum()
				self.lineplot.plot(line[:lineCount+1],clear = lineCount == 0)
				lineCount += 1
				currentIntensity =0

		self.play = False
		self.pb_stop.setEnabled(False)
		self.pb_play.setEnabled(True)

	def onMeshChanged(self,name,img,path):
		self.lbl_meshName.setText(name)
		self.lbl_meshImage.setPixmap(QPixmap(img).scaled(self.lbl_meshImage.size(),QtCore.Qt.KeepAspectRatio))
		self.mesh = Mesh.mesh.mesh