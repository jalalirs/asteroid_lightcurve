# -*- coding: utf-8 -*-



from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
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
	


class ImagePlot(FigureCanvas):
	def __init__(self,parent,width=5,height=5,back_color="white"):
		self.fig = Figure(figsize=(width,height),dpi=100)
		self.fig.patch.set_facecolor(back_color)
		FigureCanvas.__init__(self,self.fig)
		FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self._ax = self.fig.gca()

	def plot(self,img,clear=False,maxy=None,title=None):
		if clear:
			self._ax.clear()
		self._ax.imshow(img)
		if title:
			self._ax.set_title(title)
		self.fig.tight_layout()
		self.draw()
		self.flush_events()