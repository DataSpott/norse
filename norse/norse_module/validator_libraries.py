from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPalette, QColor, QIcon, QPixmap, QValidator

class Validator(QtGui.QValidator):  #creates a class called "Validator" to restict input for flowcells, barcode- and sequencing-kits
    def validate(self, string, pos):    #defines function "validated" taking any class variables ("self") and two variables "string" & "pos"
        return QtGui.QValidator.Acceptable, string, pos