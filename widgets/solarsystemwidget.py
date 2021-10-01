# -*- coding: utf-8 -*-



from . import qt_util as qtutil

from .lightcurveplot import LightCurvePlot
from .imgplot import ImagePlot
from .orbitplotter import OrbitPlot
from .mesh import Mesh
from .lightcurve import LightCurve
from voxlib.voxelize import voxelize, get_intersecting_voxels_depth_first, scale_and_shift_triangle



import numpy as np
import os
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

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QIcon, QPixmap



DIR = os.path.abspath(os.path.dirname(__file__))
QSolarSystemWidget, Ui_SolarSystemWidget = uic.loadUiType(os.path.join(DIR, "solarsystemwidget2.ui"), resource_suffix='') 


import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import dblquad
from scipy.integrate import tplquad
import pandas as pd








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
class SolarSystemWidget(QSolarSystemWidget,Ui_SolarSystemWidget):
	def __init__(self,parent):
		QWidget.__init__(self,parent)
		self.setupUi(self)
		
		self._presets = {"Mars": Mars}
		
		self.object = None

		self.__init_plots()
		self.scene = None
		self.scene =  pyrender.Scene()
		
		self.cameraNode = None
		self.meshNode = None
		self.sunLightNode = None

		self.r = pyrender.OffscreenRenderer(400, 400)
		self.mesh = None
		self.play = False

		self.lineX = None
		self.lineY = None
		self.currentStart = None
		self.minY = None
		self.maxY = None

		Mesh.mesh.signal.connect(self.onMeshChanged)
	def calculateStability(self):
		resolution = 11
		print("calculateStability")
		objfile = Mesh.mesh.path
		coords = np.array(list(set(voxelize(objfile, resolution))))

		#coords[[1, 2]] = coords[[2, 1]]
		coords = coords/max(coords.ravel())
		x, y, z  = coords[:,0],coords[:,1],coords[:,2]


		# x_mean, y_mean = np.mean(x), np.mean(y)
		# z_max = max(z)
		# P0 = x0, y0, z0 = x_mean, y_mean, z_max
		# coords = coords - P0
		# #coords = coords.T
		# x, y, z  = coords[:,0],coords[:,1],coords[:,2]


		N = coords.shape[1]
		Ix = sum(coords[1]**2 + coords[2]**2)/N
		Iy = sum(coords[0]**2 + coords[2]**2)/N
		Iz = sum(coords[0]**2 + coords[1]**2)/N
		Ixy = sum(coords[0]*coords[1])/N
		Iyz = sum(coords[1]*coords[2])/N
		Ixz = sum(coords[0]*coords[2])/N
		Wx, Wy,Wz = float(self.ln_iwX.text()),float(self.ln_iwY.text()),float(self.ln_iwZ.text())
		if Wx > Wy and Wx > Wz:
			maxVel = 1
		elif Wy > Wx and Wy > Wz:
			maxVel = 2
		else:
			maxVel = 3

		if Ix > Iy and Ix > Iz:
			maxInertia = 1
		elif Iy > Ix and Iy > Iz:
			maxInertia = 2
		else:
			maxInertia =3
		print("calculateStability")
		return maxVel == maxInertia
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
		

		self.lineplot = LightCurvePlot(self.lineCurveWidget,width = self.lineCurveWidget.width(),
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
		self.pb_showObserved.setEnabled(False)
		self.pb_normalize.setEnabled(False)
		self.pb_shiftLeft.setEnabled(False)
		self.pb_shiftRight.setEnabled(False)
		self.pb_normalize.setChecked(False)
		self.pb_showObserved.setChecked(False)


		self.play = True
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
		
		lightType = self.cmb_lightType.currentText()
		lightStrength = float(self.ln_lightIntensity.text())
		if lightType == "Point":
			light = pyrender.light.PointLight((1,1,1),lightStrength)
		elif lightType == "Directional":
			light = pyrender.light.DirectionalLight((1,1,1),lightStrength)
		elif lightType == "Spot":
			light = pyrender.light.SpotLight((1,1,1),lightStrength)
		
		self.sunLight = light
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
		if dt > period:
			notify("Dt should smaller than period","error")
			return
		shutterSpeed = float(self.ln_shutterSpeed.text())
		wX,wY,wZ = float(self.ln_wX.text()),float(self.ln_wY.text()),float(self.ln_wZ.text())
		
		time = 0
		shotTime = 0
		y = []
		currentIntensity = 0
		self.lineY = np.array([0]*int(period/shutterSpeed))
		self.lineX = np.array([0]*int(period/shutterSpeed))
		lineCount = 0
		self.currentStart = 0
		self.currentEnd = self.lineY.size
		while time < period and self.play:
			time += dt
			shotTime += dt
			meshRotX,meshRotY,meshRotZ = meshRotX+dt*wX,meshRotY+dt*wY,meshRotZ+dt*wZ
			meshPose = np.matmul(tran(meshPosX,meshPosY,meshPosZ),
			rot(rad(meshRotX),rad(meshRotY),rad(meshRotZ)))
			self.scene.set_pose(self.meshNode, pose=meshPose)
			
			color, depth = self.r.render(self.scene)
			color = color.copy()
			color[depth == 0] = 0
			currentIntensity += color.sum()
			self.renderedImagePlot.plot(color,clear=True)
			if shotTime >= shutterSpeed and lineCount < self.lineY.size:
				shotTime = 0
				self.lineY[lineCount] = currentIntensity
				self.lineX[lineCount] = time
				self.lineplot.plot(self.lineX[:lineCount+1],self.lineY[:lineCount+1],clear = lineCount == 0,color="blue")
				lineCount += 1
				currentIntensity =0
		#self.lineY = 1/self.lineY
		# in case it was stopped
		self.lineX = self.lineX[:lineCount]
		self.lineY = self.lineY[:lineCount]
		self.minY = self.lineY.min()
		self.maxY = self.lineY.max()
		
		self.play = False
		self.pb_stop.setEnabled(False)
		self.pb_play.setEnabled(True)
		self.pb_showObserved.setEnabled(True)
		self.pb_normalize.setEnabled(True)
		if self.lineX.size > 1:
			self.pb_shiftLeft.setEnabled(True)
		self.pb_shiftRight.setEnabled(False)
	
	def on_pb_shiftLeft_released(self):
		self.currentStart = self.currentStart + 1
		if self.currentStart + 1 == self.lineY.size-1:
			self.pb_shiftLeft.setEnabled(False)
		if self.currentStart != 0:
			self.pb_shiftRight.setEnabled(True)
		self.plot()
	
	def on_pb_shiftRight_released(self):
		self.currentStart = self.currentStart - 1
		if self.currentStart == 0:
			self.pb_shiftRight.setEnabled(False)
		if self.currentStart != self.lineY.size-1:
			self.pb_shiftLeft.setEnabled(True)
		self.plot()
	
	def on_pb_normalize_released(self):
		self.plot()

	def plot(self):
		simulatedX = self.lineX
		simulatedY = self.lineY
		observedX = []
		observedY = []
		if LightCurve.inUse is not None:
			lightcurve = LightCurve.inUse
			jds = lightcurve.jd
			jdmin = Time(jds[0],format="jd").to_datetime()
			observedX = [0]
			for jd in jds[1:]:
				observedX.append((Time(jd,format="jd").to_datetime()-jdmin).seconds)
			observedX = np.array(observedX)
			observedY = np.array(lightcurve.mag)
			observedY = observedY.max() - (observedY - observedY.min())
		if self.pb_normalize.isChecked():
			observedY = (observedY-observedY.min())/(observedY.max()-observedY.min())
			simulatedY = (self.lineY-self.minY)/(self.maxY-self.minY)
		simulatedX = simulatedX[0:simulatedX.size-self.currentStart]
		simulatedY = simulatedY[self.currentStart:]
		self.lineplot.plot(simulatedX,simulatedY,clear = True,color="blue")
		if self.pb_showObserved.isChecked():
			self.lineplot.plot(observedX,observedY,dot=True,clear = False,color="red")

	def on_pb_showObserved_released(self):
		if LightCurve.inUse is None:
			notify("No observed data loaded")
			self.pb_showObserved.setChecked(False)
			return
		self.plot()
				
	def on_pb_checkStability_released(self):
		if Mesh.mesh.path is None:
			qtutil.notify("You need to load a mesh first")
			return
		self.lbl_stability.setText("")
		if self.calculateStability():
			self.lbl_stability.setText("Object is stable")
		else:
			self.lbl_stability.setText("Object is not stable")
	
	def onMeshChanged(self,name,img,path):
		self.lbl_meshName.setText(name)
		self.lbl_meshImage.setPixmap(QPixmap(img).scaled(self.lbl_meshImage.size(),QtCore.Qt.KeepAspectRatio))
		self.mesh = Mesh.mesh.mesh