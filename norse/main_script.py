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
from .norse_module.MainWindow_libraries import MyWindow, VERSION

program = "norse"

def main(sysargs = sys.argv[1:]):   #main function to run script and see version
    #set up argparse for console usage
    parser = argparse.ArgumentParser(prog = program,
    description='norse, nanopore sequencing data transfer',
    usage='''norse [options]''')

    parser.add_argument("-v", "--version", action = 'version', version = f"norse = {VERSION}")
    parser.add_argument("-r", "--run", action = 'store_true', help = f"run {program}")

    if len(sysargs) < 1:  #if no arguments typed print help and exit
        parser.print_help()
        sys.exit(-1)
    else:
        args = parser.parse_args(sysargs)
    args = parser.parse_args()

    #try to download latest Seq- & Barcode-kit and Flowcell type info from OSF-archive https://osf.io/e6mpy/?view_only=
    BARCODE_KIT_EXIT_CODE = os.system(f"wget -q https://osf.io/69fuw/download -O /download/barcoding_kit_data_latest.txt")
    FLOWCELL_TYPE_EXIT_CODE = os.system(f"wget -q https://osf.io/xfn7y/download -O /download/flowcell_data_latest.txt")
    SEQ_KIT_EXIT_CODE = os.system(f"wget -q https://osf.io/ruyxz/download -O /download/sequencing_kit_data_latest.txt")

    #if downloads were successful replace original files with downloaded files
    if BARCODE_KIT_EXIT_CODE == 0:
        os.system(f"mv -f /download/barcoding_kit_data_latest.txt /norse/data/barcoding_kit_data.txt")
    if FLOWCELL_TYPE_EXIT_CODE == 0:
        os.system(f"mv -f /download/flowcell_data_latest.txt /norse/data/flowcell_data.txt")
    if SEQ_KIT_EXIT_CODE == 0:
        os.system(f"mv -f /download/sequencing_kit_data_latest.txt /norse/data/sequencing_kit_data.txt")

    if args.run:
        window()    #exec function to show MainWindow-GUI when using "-r" or "--run"


def window():   #def function to show GUI and exit correctly
    app = QApplication(sys.argv)
    
    #define and apply dark mode palette
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

    WIN = MyWindow()    #create instance of "MyWindow"-class, which is defined in MainWindow_libraries.py
    WIN.show()  #shows the instance
    sys.exit(app.exec_())


if __name__ == '__main__':  #tells program it is executed as mainscript and not as imported module -> only then "main()" is executed
    main()