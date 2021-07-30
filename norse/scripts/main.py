#!/usr/bin/env python3
import sys
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog,  QFileDialog, QFrame, QMessageBox
from PyQt5.QtGui import QPalette, QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QFileInfo
import pandas as pd
import io
import requests
import os.path
from datetime import datetime
import paramiko
import socket
import time
import os
import argparse
#from scripts import barcode_input, data_transfer_between_windows, flowcell_barcode_sequencing_kits, mainWindow, sample_upload, upload_data, window2
#import scripts.mainWindow as mw
import hulu
from mainWindow import iniUI

version = "0.2"
program = "norse"


file_1 = 0
upload_sample_path = 0

"""
def main(sysargs = sys.argv[1:]):#main function to run script and see version
    
    parser = argparse.ArgumentParser(prog = program,
    description='norse, nanopoore sequencing data transfer',
    usage='''norse [options]''')

    
    parser.add_argument("-v","--version", action='version', version=f"norse= {version}")
    parser.add_argument("-r","--run",action='store_true', help=f"run {program}")
        
    if len(sysargs)<1:#if nothing typed show all arguments which avaible
        parser.print_help()
        sys.exit(-1)
    else:
        args = parser.parse_args(sysargs)
    args = parser.parse_args()
    
    if args.run:
        window()#function to show GUI
    
"""    
class Validator(QtGui.QValidator):#validator to restict input for flowcells,barcode and sequencinkits
    def validate(self, string, pos):
        return QtGui.QValidator.Acceptable, string.upper(), pos

class Window2(QMainWindow):#class for window2 (pop up window)
    def __init__(self):
        super(Window2,self).__init__()
        self.setWindowTitle("check your data")
        self.setGeometry(400, 400, 330, 385)
        #self.iniUI()
class MyWindow(QMainWindow):#create a window through the initUI() method, and call it in the initialization method init()
    
    def __init__(self):
        super(MyWindow, self).__init__()
        
        #self.secondwindow = Window2()
        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle('norse')
        self.window2 = Window2()
        iniUI(self)
        
        
def window():# func to show GUI and exit correctly
    app = QApplication(sys.argv)
    
    
    # dark mode pallette
    app.setStyle('Fusion')
    dark_palette = QtGui.QPalette()

    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)

    app.setPalette(dark_palette)

    win = MyWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':#to clarify this has to be mainscript and not a importet module
    #main()
    window()