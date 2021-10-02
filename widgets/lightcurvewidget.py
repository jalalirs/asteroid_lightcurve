

import os
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtCore import Qt,QObject


import glob
from .qt_util import notify
from .lightcurveplot import LightCurvePlot
from .lightcurve import LightCurve

import requests
from bs4 import BeautifulSoup as bs
import numpy as np 

# defining the api-endpoint 
API_ENDPOINT = "https://alcdef.org/php/alcdef_GenerateALCDEFPage.php"


DIR = os.path.abspath(os.path.dirname(__file__))
QLightCurveWidget, Ui_LightCurveWidget = uic.loadUiType(os.path.join(DIR, "lightcurveWidget.ui"), resource_suffix='') 



class RetrieveWorker(QObject):
    retrievingCompleted = QtCore.pyqtSignal(list)

    def __init__(self):
        super(RetrieveWorker, self).__init__()

    def get_lcs(self,objectId):
        data = {'doSearch2':"Display",
            #'checkall':'on',
            'selectedObject':objectId}
        r = requests.post(url = API_ENDPOINT, data = data)
        content = r.content
        soup = bs(content ,'html.parser')

        data = soup.findAll('input', {'name': "plotLC"})
        lcs = [d["value"] for d in data]
        return lcs
    def get_data(self,objectId,lcs):
        data = {'saveLC':"Download",
                'checkall':'on',
                'SearchNumber':objectId,
                "lightcurves[]":lcs}
        r = requests.post(url = API_ENDPOINT, data = data)
        content = r.content
        return content
    def parse(self,text):
        lines = text.strip().splitlines()
        index = 0
        ccount = 0
        curves = []
        while index < len(lines):
            c = LightCurve(ccount)
            index += 1 # skipping STARTMETADATA
            while index < len(lines) and lines[index].strip() != "ENDMETADATA":
                index += 1
                p = lines[index].split("=")
                if len(p)==1:
                    c.metadata[p[0]] = None
                else:
                    c.metadata[p[0]] = p[1]
            index += 1
            while index < len(lines) and  lines[index].strip() != "ENDDATA":
                p = lines[index].split("|")
                
                c.jd.append(float(p[0].split("=")[-1]))
                c.mag.append(float(p[1]))
                c.err.append(float(p[2]))
                index += 1
            
            ccount += 1
            if len(c.jd) > 0:
                curves.append(c)
            index +=1
        return curves
    def run(self,objid):
        lcs = self.get_lcs(objid)
        data = self.get_data(objid,lcs).decode("utf-8")
        items = self.parse(data)
        self.retrievingCompleted.emit(items)

class LightCurveWidget(QLightCurveWidget, Ui_LightCurveWidget):
    retrieveRequested = QtCore.pyqtSignal(str)
    def __init__(self,parent=None):
        super(LightCurveWidget,self).__init__(parent)
        self.setupUi(self)
        self.__init_plots()
        self.progressBar.setVisible(False)

        self._rthread = QtCore.QThread()
        self._rworkder = RetrieveWorker()
        self._rworkder.moveToThread(self._rthread)
        self.retrieveRequested.connect(self._rworkder.run)
        self._rworkder.retrievingCompleted.connect(self.on_retrieve_completed)
        #TODO: create new thread upon clicking
        self._rthread.start()
        self.items = []
        self.currentRow = None

    def __init_plots(self):	
        self.lightcurveplot = LightCurvePlot(self.lightCurveWidget,width = self.lightCurveWidget.width(),
            height=self.lightCurveWidget.height())
        self.lightCurveLayout.addWidget(self.lightcurveplot)
    
    def on_lst_runs_currentRowChanged(self,row):
        selectedItem = self.items[row]
        self.currentRow = row

        self.lightcurveplot.plot(np.array(selectedItem.jd),np.array(selectedItem.mag),np.array(selectedItem.err),flipy=True)

    def on_pb_retrieve_released(self):
        objid = self.ln_objId.text().strip()
        if len(objid) == 0:
            return
        self.pb_retrieve.setEnabled(False)
        self.progressBar.setVisible(True)
        self.pb_use.setEnabled(False)
        self.retrieveRequested.emit(objid)
    
    def on_retrieve_completed(self,items):
        self.lst_runs.clear()
        self.items = items
        if len(items) > 0 :
            self.pb_use.setEnabled(True)
            if "OBJECTNAME" in items[0].metadata:
                self.lbl_objectName.setText(f'{items[0].metadata["OBJECTNAME"]}')
        for item in items:
            self.lst_runs.addItem(f'{item.metadata["LCBLOCKID"]} ({item.metadata["SESSIONDATE"]})')
         
        self.pb_retrieve.setEnabled(True)
        self.progressBar.setVisible(False)

    def on_pb_use_released(self):
        if self.currentRow is None:
            notify("Select a curve first","error")
            return
        selectedItem = self.items[self.currentRow]
        LightCurve.inUse = selectedItem
        notify(f"Curve {selectedItem.metadata['LCBLOCKID']} is in use now","info")
