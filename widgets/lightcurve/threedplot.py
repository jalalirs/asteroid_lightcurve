# -*- coding: utf-8 -*-



from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import sys
import numpy as np
from matplotlib.ticker import LinearLocator
from mpl_toolkits.mplot3d import Axes3D

def resadjust(ax, ticks, ticks_labels):
	"""
	Send in an axis and I fix the resolution as desired.
	"""

	t = [i[0] for i in np.array_split(ticks,10)]
	tl = [i[0] for i in np.array_split(ticks_labels,10)]
	ax.set_xticks(t)
	ax.set_xticklabels(tl)
	ax.xaxis.set_tick_params(rotation=45)
	


class ThreeDPlot(FigureCanvas):
	def __init__(self,parent,width=5,height=5,back_color="white"):
		self.fig = Figure(figsize=(width,height),dpi=100)
		self.fig.patch.set_facecolor(back_color)
		FigureCanvas.__init__(self,self.fig)
		FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self._ax = Axes3D(self.fig)

	def plot(self,x,y,z, icons,colors,cameraDir=None,clear=False,maxy=None,title=None):
		if clear:
			self._ax.clear()
		
		self._ax.scatter(x[0],y[0],z[0],c=colors[0],marker=icons[0],s=100)
		self._ax.scatter(x[1],y[1],z[1],c=colors[1],marker=icons[1],s=100)
		self._ax.scatter(x[2],y[2],z[2],c=colors[2],marker=icons[2],s=100)

		if title:
			self._ax.set_title(title)
		self.draw()
		self.flush_events()
	