#!/usr/bin/env python
#
import PyQt5

import sys

from PyQt5 import QtWidgets, QtCore, QtGui #pyqt stuff

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons
import matplotlib
matplotlib.use("Qt5Agg")
import sys
import os
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout,QApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import *


from widgets.lightcurve import CustomeSetupWidget
from widgets.lightcurve import SolarSystemWidget
import utils


DIR = os.path.abspath(os.path.dirname(__file__))
QMainWindow, Ui_MainWindow = uic.loadUiType(os.path.join(DIR, "widgets/mainwindow.ui"), resource_suffix='') 

import resources.resources_rc

class AstroidCurve(QMainWindow, Ui_MainWindow):
	def __init__(self,parent=None):
		super(AstroidCurve,self).__init__(parent)
		self.setupUi(self)
		stream = QFile('resources/styles/ALightCurve.css')
		if stream.open(QIODevice.ReadOnly | QFile.Text):
			self.setStyleSheet(QTextStream(stream).readAll())
		
		solarSystemWidget = SolarSystemWidget(self)
		self._solarSystemWidget = solarSystemWidget
		earthLayout = QVBoxLayout()
		earthLayout.addWidget(solarSystemWidget)
		self.pageEarth.setLayout(earthLayout)

		# trainingWidget = TrainingWidget(self)
		# self._trainingWidget = trainingWidget
		# trainingLayout = QVBoxLayout()
		# trainingLayout.addWidget(trainingWidget)
		# self.pageTrain.setLayout(trainingLayout)

		customeSetupWidget = CustomeSetupWidget(self)
		self._customeSetupWidget = customeSetupWidget
		lightlayout = QVBoxLayout()
		lightlayout.addWidget(customeSetupWidget)
		self.pageLight.setLayout(lightlayout)

		#self.on_pbData_released()
		self.mainStackedWidget.setCurrentIndex(0)
		self.uncheck_and_keep(0)

	def uncheck_and_keep(self,keepindex):
		toolbarButtons = self.toolbarWidget.findChildren(QtWidgets.QPushButton)
		for i,b in enumerate(toolbarButtons):
			if i != keepindex:
				b.setChecked(False)
			else:
				b.setChecked(True)


	def on_pbLight_released(self):
		self.mainStackedWidget.setCurrentIndex(0)
		self.uncheck_and_keep(0)
	def on_pbEarth_released(self):
		self.mainStackedWidget.setCurrentIndex(1)
		self.uncheck_and_keep(1)
	def on_pbTest_released(self):
		self.mainStackedWidget.setCurrentIndex(2)
		self.uncheck_and_keep(2)
	def on_pbTrain_released(self):
		self.mainStackedWidget.setCurrentIndex(3)
		self.uncheck_and_keep(3)
	
	def on_pbDeploy_released(self):
		self.mainStackedWidget.setCurrentIndex(4)
		self.uncheck_and_keep(4)


def except_hook(cls,exception,traceback):
	sys.__excepthook__(cls,exception,traceback)


def main():
	import sys
	sys.excepthook = except_hook
	app = QtWidgets.QApplication(sys.argv)
	form = AstroidCurve()
	form.show()
	sys.exit(app.exec_())
if __name__ == '__main__':
	
	main()

