import sys
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog,  QFileDialog, QFrame, QMessageBox
from PyQt5.QtGui import QPalette, QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QFileInfo
import pandas as pd
import numpy as np
import re

class Window2(QMainWindow): #class for window2 (pop up window)
    
    def __init__(self):
        super(Window2,self).__init__()
        #set up window title and geometry
        self.setWindowTitle("check your data")
        self.setGeometry(400, 400, 330, 385)

        #set up two lists containing "LABEL1" to "LABEL24" or "INPUT1" to "INPUT24"
        self.LABEL_NAME_LIST = ["LABEL" + str(ITEM) for ITEM in list(range(1, 25, 1))]
        self.INPUT_NAME_LIST = ["INPUT" + str(ITEM) for ITEM in list(range(1, 25, 1))]
        self.iniUI()


    def iniUI(self):
        globs, locs = globals(), locals()   #get global & local variables

        #list comprehension to set up 24 labels called LABEL1 to LABEL24 and INPUT1 to INPUT24
        [exec(f"self.{LABEL_NAME} = QtWidgets.QLabel(self)", globs, locs) for LABEL_NAME in self.LABEL_NAME_LIST]
        [exec(f"self.{INPUT_NAME} = QtWidgets.QLabel(self)", globs, locs) for INPUT_NAME in self.INPUT_NAME_LIST]
        
        #set up Table widget & hide it -> getting filled by "open_sheet"-function
        self.WIDGET_TABLE_VIEW = QtWidgets.QTableWidget(self)
        self.WIDGET_TABLE_VIEW.setHidden(True)
        self.WIDGET_TABLE_VIEW.move(15,100)
        self.WIDGET_TABLE_VIEW.setMinimumWidth(300)
        self.WIDGET_TABLE_VIEW.setMaximumWidth(300)
        self.WIDGET_TABLE_VIEW.setMinimumHeight(245)
        self.WIDGET_TABLE_VIEW.setMaximumHeight(245)

        #define coordinates for each "LABEL"- & "INPUT"-label & move them to according positions
        LABEL_X_Y_COORDS = []
        INPUT_X_Y_COORDS = []
        Y_COORD = 70
        INPUT_X_COORD = 20
        for i in range(1,25,1):
            if i < 10:
                LABEL_X_COORD = 10
            elif 9 < i <= 12:
                LABEL_X_COORD = 6
            elif i == 13:
                INPUT_X_COORD = 200
                LABEL_X_COORD = 180
                Y_COORD = 70
            Y_COORD += 20
            LABEL_X_Y_COORDS.append([LABEL_X_COORD, Y_COORD])
            INPUT_X_Y_COORDS.append([INPUT_X_COORD,Y_COORD])

        [exec(f"self.{self.LABEL_NAME_LIST[INDEX]}.move(*{LABEL_X_Y_COORDS[INDEX]})",globs, locs) for INDEX in range(len(self.LABEL_NAME_LIST))]
        [exec(f"self.{self.INPUT_NAME_LIST[INDEX]}.move(*{INPUT_X_Y_COORDS[INDEX]})",globs, locs) for INDEX in range(len(self.INPUT_NAME_LIST))]

        #list comprehension to set text for each "LABEL"-label
        [exec(f"self.{self.LABEL_NAME_LIST[INDEX]}.setText(str({INDEX} + 1))",globs, locs) for INDEX in range(len(self.LABEL_NAME_LIST))]
        
        #set up labels and move them to according positions -> "INPUT" named labels get their text from function "passinInformation" in MainWindow_libraries.py
        self.LABEL_SAMPLE = QtWidgets.QLabel(self)
        self.LABEL_SAMPLE.setText('sample name:')
        self.LABEL_SAMPLE.move(20, 70)
        
        self.LABEL_SEQ_KIT = QtWidgets.QLabel(self)
        self.LABEL_SEQ_KIT.move(20, 10)
        self.LABEL_SEQ_KIT.setText('kit:')
        self.INPUT_SEQ_KIT = QtWidgets.QLabel(self)
        self.INPUT_SEQ_KIT.resize(200, 30)
        self.INPUT_SEQ_KIT.move(115, 10)

        self.LABEL_BARCODE_KIT = QtWidgets.QLabel(self)
        self.LABEL_BARCODE_KIT.move(20, 30)
        self.LABEL_BARCODE_KIT.setText('barcoding kit:')
        self.INPUT_BARCODE_KIT = QtWidgets.QLabel(self)
        self.INPUT_BARCODE_KIT.resize(200, 30)
        self.INPUT_BARCODE_KIT.move(115, 30)
        
        self.LABEL_FLOWCELL_TYPE = QtWidgets.QLabel(self)
        self.LABEL_FLOWCELL_TYPE.move(20, 50)
        self.LABEL_FLOWCELL_TYPE.setText('flowcell:')
        self.INPUT_FLOWCELL_TYPE = QtWidgets.QLabel(self)
        self.INPUT_FLOWCELL_TYPE.resize(200, 30)
        self.INPUT_FLOWCELL_TYPE.move(115, 50)

        #set up pushbutton to close window
        self.PUSHBUTTON_CLOSE = QtWidgets.QPushButton(self)
        self.PUSHBUTTON_CLOSE.setText('ok!')
        self.PUSHBUTTON_CLOSE.move(230, 355)
        self.PUSHBUTTON_CLOSE.clicked.connect(self.close)   #closes window2


    def hide_and_show(self, first_label_index, last_label_index, BOOLEAN):  #function to hide/show labels and inputs
        globs, locs = globals(), locals()
        #list comprehension to execute command "self.LABELX.setHidden(BOOLEAN)" for each Label and Input name -> Boolean is either true or false
        [exec(f'self.{LABEL_NAME}.setHidden({BOOLEAN})', globs,locs) for LABEL_NAME in self.LABEL_NAME_LIST[(first_label_index - 1):last_label_index]]
        [exec(f'self.{INPUT_NAME}.setHidden({BOOLEAN})', globs,locs) for INPUT_NAME in self.INPUT_NAME_LIST[(first_label_index - 1):last_label_index]]
        self.WIDGET_TABLE_VIEW.setHidden(True)


    def open_sheet(self):
        #SAMPLE_INFO_FILE_SUFFIX = global variable -> suffix (.csv, .tsv, .xlsx) of the uploaded sample information sheet (barcode, sampleID)     
        if self.SAMPLE_INFO_FILE_SUFFIX == 'xlsx':
            SAMPLE_INFO_DF = pd.read_excel(self.SAMPLE_INFO_FILE_PATH, header = None)
        
        elif self.SAMPLE_INFO_FILE_SUFFIX == 'csv':
            SAMPLE_INFO_DF = pd.read_csv(self.SAMPLE_INFO_FILE_PATH, sep = ',', header = None)
        
        elif self.SAMPLE_INFO_FILE_SUFFIX == 'tsv':
            SAMPLE_INFO_DF = pd.read_csv(self.SAMPLE_INFO_FILE_PATH, header = None)
            
        SAMPLE_INFO_DF_CLEANED = SAMPLE_INFO_DF.fillna(value = "NaN").replace(r'^\s*$', "NaN", regex = True)

        self.WIDGET_TABLE_VIEW.setColumnCount(2)
        self.WIDGET_TABLE_VIEW.setRowCount(0)

        for ROWS in range(0, len(SAMPLE_INFO_DF_CLEANED)):
            BARCODE = SAMPLE_INFO_DF_CLEANED.loc[ROWS, 0]
            SAMPLE_NAME = str(SAMPLE_INFO_DF_CLEANED.loc[ROWS, 1])
            
            if BARCODE != "barcode":
                BARCODE_CLEANED = str(re.sub('[^0-9]', '', BARCODE))
            else:
                BARCODE_CLEANED = BARCODE
            
            if SAMPLE_NAME != "NaN":    #skip lines without sample_id
                self.WIDGET_TABLE_VIEW.insertRow(self.WIDGET_TABLE_VIEW.rowCount()) #add new row to the QTWidget_Table
                self.WIDGET_TABLE_VIEW.setItem((self.WIDGET_TABLE_VIEW.rowCount() - 1), 0, QtWidgets.QTableWidgetItem(BARCODE_CLEANED)) #add according barcode to first column of last row
                self.WIDGET_TABLE_VIEW.setItem((self.WIDGET_TABLE_VIEW.rowCount() - 1), 1, QtWidgets.QTableWidgetItem(SAMPLE_NAME))

        self.WIDGET_TABLE_VIEW.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.WIDGET_TABLE_VIEW.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.WIDGET_TABLE_VIEW.setHidden(False)
        self.WIDGET_TABLE_VIEW.show


    def displayInfo(self):  #shows window2
        self.show( )