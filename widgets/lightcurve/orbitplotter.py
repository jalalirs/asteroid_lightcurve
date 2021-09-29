# -*- coding: utf-8 -*-



from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from poliastro.plotting import StaticOrbitPlotter
import sys
import numpy as np

def resadjust(ax, ticks, ticks_labels):
	"""
	Send in an axis and I fix the resolution as desired.
	"""

	t = [i[0] for i in np.array_split(ticks,10)]
	tl = [i[0] for i in np.array_split(ticks_labels,10)]
	ax.set_xticks(t)
	ax.set_xticklabels(tl)
	ax.xaxis.set_tick_params(rotation=45)
	


class OrbitPlot(FigureCanvas):
	def __init__(self,parent,width=5,height=5,back_color="white"):
		self.fig = Figure(figsize=(width,height),dpi=100)
		self.fig.patch.set_facecolor(back_color)
		FigureCanvas.__init__(self,self.fig)
		FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self._ax = self.fig.add_subplot(111)
		self.plotter = StaticOrbitPlotter(self._ax)
		self.objects = []
		self.currentCanvasSize = None


	def plot(self,earth,body,epoch, labels,clear=False):
		if clear:
			self._ax.clear()
		self.currentCanvasSize = self.fig.get_size_inches()
		#for obj,lbl in zip(objs,labels):
		earth_t,earth_p = self.plotter.plot_body_orbit(earth,epoch,label=labels[0])
		body_t,body_p = self.plotter.plot_body_orbit(body,epoch,label=labels[1])
		
		self.fig.tight_layout()
		#self.fig.set_size_inches()
		self.fig.set_size_inches(self.currentCanvasSize)
		self.draw()
		self.flush_events()
		return earth_t,earth_p,body_t,body_p