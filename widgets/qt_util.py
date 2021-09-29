
from PyQt5 import QtCore, QtGui, uic
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication,QMessageBox
import os


def clear_layout(layout):
	for i in reversed(range(layout.count())): 
		item = layout.takeAt(i).widget()
		if item is not None:
		 	item.deleteLater()

def _error(msg):
	msgBox = QMessageBox()
	msgBox.setIcon(QMessageBox.Critical)
	msgBox.setText(msg)  	
	msgBox.setWindowTitle("Alert")
	msgBox.setStandardButtons(QMessageBox.Close)
	retval = msgBox.exec_()

def notify(msg,ntype="error"):
	if ntype == "error":
		_error(msg)
def getDirBrowser():
	dialog = QtWidgets.QFileDialog()
	dialog.setFileMode(QtWidgets.QFileDialog.Directory)
	dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
	directory = dialog.getExistingDirectory(None, 'Choose Directory', os.path.curdir)
	return str(directory)
def saveFileBrowser():
	fileName = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Project', '.')
	return fileName[0]
def openFileBrowser():
	fileName = QtWidgets.QFileDialog.getOpenFileName(None, 'Open Project', '.')
	return fileName[0]
def browse(btype = "folder"):
	if btype == "folder":
		return getDirBrowser()
	elif btype == "savefile":
		return saveFileBrowser()
	elif btype == "openfile":
		return openFileBrowser()


