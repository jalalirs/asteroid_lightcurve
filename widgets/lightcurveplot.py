# -*- coding: utf-8 -*-



from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import LinearLocator

def resadjust(ax, ticks, ticks_labels):
	"""
	Send in an axis and I fix the resolution as desired.
	"""

	t = [i[0] for i in np.array_split(ticks,10)]
	tl = [i[0] for i in np.array_split(ticks_labels,10)]
	ax.set_xticks(t)
	ax.set_xticklabels(tl)
	ax.xaxis.set_tick_params(rotation=45)
	


class LightCurvePlot(FigureCanvas):
	def __init__(self,parent,width=5,height=5,back_color="white"):
		self.fig = Figure(figsize=(width,height),dpi=100)
		self.fig.patch.set_facecolor(back_color)
		FigureCanvas.__init__(self,self.fig)
		FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self._ax = self.fig.gca()

	def plot(self,x,y,error=None,dot=False,xticks=None,color="red",clear=False,maxy=None,title=None):
		if clear:
			self._ax.clear()
		if not maxy:
			maxy = y.max()*1.05
		self._ax.set_ylim(y.min()*0.95,maxy)
		self._ax.set_xlim(x.min(),x.max())

		if error is not None:
			self._pts = self._ax.errorbar(x,y,yerr=error, fmt='ro',c=color)
		elif dot:
			self._pts = self._ax.plot(x,y,'ro',c=color)
		else:
			self._pts = self._ax.plot(x,y,c=color)

		self._ax.invert_yaxis()

		if xticks is not None:
			resadjust(self._ax,x,xticks)
		if title:
			self._ax.set_title(title)
		self.draw()
		self.flush_events()
	