#functions defining main Window GUI and In-/Outputs

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
from .Window2_libraries import *
from .validator_libraries import *
from pathlib import Path

VERSION = "1.0.0"

class MyWindow(QMainWindow):    #create a window through the initUI() method, and call it in the initialization method init()
    
    def __init__(self): #'self' is the first parameter of a class' methods that refers to the actual instance of the class
        super(MyWindow, self).__init__()
        
        #define window geometry and title
        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle('norse')
        
        #create two lists of 24 strings each, called "LABEL1"/"LINEEDIT1" to "LABEL24"/"LINEEDIT24" -> a label is a text element shown in the GUI
        self.LABEL_NAME_LIST_MAIN = ["LABEL" + str(NUMBER) for NUMBER in list(range(1, 25, 1))] # list(range(1,25,1)) creates list from 1 to 24
        self.INPUT_NAME_LIST_MAIN = ["LINEEDIT" + str(NUMBER) for NUMBER in list(range(1, 25, 1))]
        
        self.UPLOAD_SAMPLE_PATH = "0"
        self.iniUI()    #function call


    def iniUI(self):

        self.WINDOW2 = Window2()    #initiate window2
        HOME = str(Path.home())
        self.NORSE_USER_INFO_PATH = HOME + "/norse_user_info.txt"
        globs, locs = globals(), locals()
        [exec(f"self.{LABEL_NAME} = QtWidgets.QLabel(self)",globs, locs) for LABEL_NAME in self.LABEL_NAME_LIST_MAIN]
        [exec(f"self.{INPUT_NAME} = QtWidgets.QLineEdit(self)",globs, locs) for INPUT_NAME in self.INPUT_NAME_LIST_MAIN]
        
        X_Y_COORDS_FOR_LABEL = []   #set up empty list
        X_Y_COORDS_FOR_INPUT = []
        Y_COORD = 20 #initial label y-coord
        for i in range(1,25,1): #loop over 24 numbers to adjust x and y coords to set up two columns with 12 label and input fields each
            if i == 1:
                LABEL_X_COORD = 245
                INPUT_X_COORD = 260
            elif i < 13:
                Y_COORD += 30
            elif i == 13:
                LABEL_X_COORD = 533
                INPUT_X_COORD = 550
                Y_COORD = 20
            elif i > 13:
                Y_COORD += 30
            X_Y_COORDS_FOR_LABEL.append([LABEL_X_COORD,Y_COORD])
            X_Y_COORDS_FOR_INPUT.append([INPUT_X_COORD,Y_COORD])

        #create label and input fields with names and coords
        [exec(f"self.{self.LABEL_NAME_LIST_MAIN[INDEX]}.move(*{X_Y_COORDS_FOR_LABEL[INDEX]})",globs, locs) for INDEX in range(0, len(self.LABEL_NAME_LIST_MAIN))]
        [exec(f"self.{self.INPUT_NAME_LIST_MAIN[INDEX]}.move(*{X_Y_COORDS_FOR_INPUT[INDEX]})",globs, locs) for INDEX in range(0, len(self.INPUT_NAME_LIST_MAIN))]
        
        #set mock-text for each label and input field
        [exec(f"self.{self.LABEL_NAME_LIST_MAIN[INDEX]}.setText(str({INDEX}+ 1))",globs, locs) for INDEX in range(0, len(self.LABEL_NAME_LIST_MAIN))]
        [exec(f'self.{INPUT_NAME}.resize(240,30)', globs,locs) for INPUT_NAME in self.INPUT_NAME_LIST_MAIN[(1-1):24]]

        #hide all label and input fields on initialization
        [exec(f'self.{LABEL_NAME}.setHidden(True)', globs,locs) for LABEL_NAME in self.LABEL_NAME_LIST_MAIN[(1-1):24]]
        [exec(f'self.{INPUT_NAME}.setHidden(True)', globs,locs) for INPUT_NAME in self.INPUT_NAME_LIST_MAIN[(1-1):24]]

        #show first label and input field upon initialization
        self.LABEL1.setHidden(False)   
        self.LINEEDIT1.setHidden(False)

        #set up field for dir input
        self.INPUT_DIR_NAME = QtWidgets.QLineEdit(self)  #create instance of wanted class in the QtWidgets-package 
        self.INPUT_DIR_NAME.setPlaceholderText('your directory name (optional)')  #set mock text
        self.INPUT_DIR_NAME.move(5, 10)  #move field to specified position
        self.INPUT_DIR_NAME.setFixedWidth(210)   #declare fixed width of field

        #set up frames in window
        self.UPPER_FRAME = QtWidgets.QFrame(self)
        self.UPPER_FRAME.setFixedWidth(210)
        self.UPPER_FRAME.setFixedHeight(145)
        self.UPPER_FRAME.move(5, 50)
        self.UPPER_FRAME.setFrameShape(QFrame.StyledPanel)
        self.UPPER_FRAME.setFrameShadow(QFrame.Raised)

        self.MID_FRAME = QtWidgets.QFrame(self)
        self.MID_FRAME.setFixedWidth(210)
        self.MID_FRAME.setFixedHeight(130)
        self.MID_FRAME.move(5, 200)
        self.MID_FRAME.setFrameShape(QFrame.StyledPanel)
        self.MID_FRAME.setFrameShadow(QFrame.Raised)

        #set up field for password input
        self.INPUT_PASSWORD = QtWidgets.QLineEdit(self)
        self.INPUT_PASSWORD.move(260, 400)
        self.INPUT_PASSWORD.setPlaceholderText('password')
        self.INPUT_PASSWORD.setEchoMode(QtWidgets.QLineEdit.Password)

        #set up button to hide/show text in password field above
        self.CHECKBOX_PASSWORD_HIDE_SHOW = QtWidgets.QCheckBox('show',self)
        self.CHECKBOX_PASSWORD_HIDE_SHOW.adjustSize()
        self.CHECKBOX_PASSWORD_HIDE_SHOW.stateChanged.connect(self.password_hide_show)
        self.CHECKBOX_PASSWORD_HIDE_SHOW.move(370, 405)

        #set up label ":"
        self.LABEL_DOUBLE_DOT = QtWidgets.QLabel(self)
        self.LABEL_DOUBLE_DOT.setText(':')
        self.LABEL_DOUBLE_DOT.adjustSize()
        self.LABEL_DOUBLE_DOT.move(250, 406)
        
        #set up label and input field for sequencing kit (with option table and self-validation)
        self.LABEL_SEQUENCING_KIT = QtWidgets.QLabel(self)
        self.LABEL_SEQUENCING_KIT.move(10, 50)
        self.LABEL_SEQUENCING_KIT.setText('Ligation kit:')

        with open('/norse/data/sequencing_kit_data.txt') as file:   #open file containing all possible sequencing kits
            SEQUENCING_KIT_LIST = [LINE.rstrip() for LINE in file]  #read all lines into list removing whitespaces
        self.INPUT_SEQUENCING_KIT = QtWidgets.QComboBox(self)    #initialize necessary class instance
        self.INPUT_SEQUENCING_KIT.setEditable(True)  #allow inputs to the field
        self.INPUT_SEQUENCING_KIT.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.INPUT_SEQUENCING_KIT.addItems(SEQUENCING_KIT_LIST)  #add list of seq-kits as options for the field
        self.INPUT_SEQUENCING_KIT.setMinimumWidth(190)
        self.INPUT_SEQUENCING_KIT.move(10, 75)
        self.validator = Validator(self)    #???
        self.INPUT_SEQUENCING_KIT.setValidator(self.validator)
        self.INPUT_SEQUENCING_KIT.lineEdit().editingFinished.connect(self.sequencing_kit_changed)    #validate field input upon writing is finished -> checks if input matches a seq-kit from the list

        #label and input field for barcode-kit (analog to seq-kit input above)
        self.LABEL_BARCODE_KIT = QtWidgets.QLabel(self)
        self.LABEL_BARCODE_KIT.move(10, 102)
        self.LABEL_BARCODE_KIT.setText('Barcode kit:')
        self.LABEL_BARCODE_KIT.adjustSize()

        with open('/norse/data/barcoding_kit_data.txt') as file:   #open file containing all possible sequencing kits
            BARCODE_KIT_LIST = [LINE.rstrip() for LINE in file]  #read all lines into list removing whitespaces
        self.INPUT_BARCODE_KIT = QtWidgets.QComboBox(self)
        self.INPUT_BARCODE_KIT.setEditable(True)
        self.INPUT_BARCODE_KIT.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.INPUT_BARCODE_KIT.addItems(BARCODE_KIT_LIST)
        self.INPUT_BARCODE_KIT.setMinimumWidth(190)
        self.INPUT_BARCODE_KIT.move(10, 120)
        self.INPUT_BARCODE_KIT.setValidator(self.validator)
        self.INPUT_BARCODE_KIT.lineEdit().editingFinished.connect(self.barcode_kit_changed)
        
        #label and input field for flowcell-type (analog to seq-kit input above)
        self.LABEL_FLOWCELL_TYPE = QtWidgets.QLabel(self)
        self.LABEL_FLOWCELL_TYPE.move(10, 140)
        self.LABEL_FLOWCELL_TYPE.setText('Flowcell:')

        with open('/norse/data/flowcell_data.txt') as file:
            FLOWCELL_TYPE_LIST = [LINE.rstrip() for LINE in file]
        self.INPUT_FLOWCELL_TYPE = QtWidgets.QComboBox(self)
        self.INPUT_FLOWCELL_TYPE.setEditable(True)
        self.INPUT_FLOWCELL_TYPE.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.INPUT_FLOWCELL_TYPE.addItems(FLOWCELL_TYPE_LIST)
        self.INPUT_FLOWCELL_TYPE.setMinimumWidth(190)
        self.INPUT_FLOWCELL_TYPE.move(10, 165)
        self.INPUT_FLOWCELL_TYPE.setValidator(self.validator)
        self.INPUT_FLOWCELL_TYPE.lineEdit().editingFinished.connect(self.flowcell_changed)

        #set up Barcode "yes" and "no" buttons - grouped, only one can be selected
        self.LABEL_BARCODE_CHOICE = QtWidgets.QLabel(self)
        self.LABEL_BARCODE_CHOICE.setText('Barcodes?')
        self.LABEL_BARCODE_CHOICE.move(10, 200)

        self.RADIOBUTTON_CHOOSE_1_SAMPLE = QtWidgets.QRadioButton(self)  #set up round button for "no"
        self.RADIOBUTTON_CHOOSE_1_SAMPLE.toggled.connect(self.radiobutton_no)  #toggle function "radiobutton_no" when button is selected
        self.RADIOBUTTON_CHOOSE_1_SAMPLE.move(10, 225)
        self.LABEL_CHOOSE_1_SAMPLE = QtWidgets.QLabel(self)
        self.LABEL_CHOOSE_1_SAMPLE.setText('no')
        self.LABEL_CHOOSE_1_SAMPLE.move(30, 225)

        self.RADIOBUTTON_CHOOSE_12_SAMPLE = QtWidgets.QRadioButton(self)
        self.RADIOBUTTON_CHOOSE_12_SAMPLE.toggled.connect(self.radiobutton_yes)
        self.RADIOBUTTON_CHOOSE_12_SAMPLE.move(10, 245)
        self.LABEL_CHOOSE_12_SAMPLE = QtWidgets.QLabel(self)
        self.LABEL_CHOOSE_12_SAMPLE.setText('yes (12)')
        self.LABEL_CHOOSE_12_SAMPLE.move(30, 245)

        #set up label hidden label used when filling the USER_PRE_INFO
        #self.LABEL_TEST_UPLOAD_VARIABLE = QtWidgets.QLabel(self)
        #self.LABEL_TEST_UPLOAD_VARIABLE.setHidden(True)

        #set up button to select input for 24 samples 
        self.RADIOBUTTON_CHOOSE_24_SAMPLES = QtWidgets.QRadioButton(self)
        self.RADIOBUTTON_CHOOSE_24_SAMPLES.toggled.connect(self.radiobutton_24)
        self.RADIOBUTTON_CHOOSE_24_SAMPLES.move(10, 265)
        self.LABEL_CHOOSE_24_SAMPLES = QtWidgets.QLabel(self)
        self.LABEL_CHOOSE_24_SAMPLES.setText('yes (24)')
        self.LABEL_CHOOSE_24_SAMPLES.move(30, 265)

        ##set up button to select input of an individual sample sheet (csv/tsv/xlsx)
        self.RADIOBUTTON_CHOOSE_SAMPLE_SHEET = QtWidgets.QRadioButton(self)
        self.RADIOBUTTON_CHOOSE_SAMPLE_SHEET.toggled.connect(self.radiobutton_96)
        self.RADIOBUTTON_CHOOSE_SAMPLE_SHEET.move(10, 285)
        self.LABEL_CHOOSE_SAMPLE_SHEET = QtWidgets.QLabel(self)
        self.LABEL_CHOOSE_SAMPLE_SHEET.setText('yes (sample sheet)')
        self.LABEL_CHOOSE_SAMPLE_SHEET.move(30, 290)
        self.LABEL_CHOOSE_SAMPLE_SHEET.resize(150, 20)

        #group buttons so only one of them is active at a time
        self.RADIOBUTTON_GROUP_CHOOSE_SAMPLES = QtWidgets.QButtonGroup(self)
        self.RADIOBUTTON_GROUP_CHOOSE_SAMPLES.addButton(self.RADIOBUTTON_CHOOSE_12_SAMPLE)
        self.RADIOBUTTON_GROUP_CHOOSE_SAMPLES.addButton(self.RADIOBUTTON_CHOOSE_1_SAMPLE)
        self.RADIOBUTTON_GROUP_CHOOSE_SAMPLES.addButton(self.RADIOBUTTON_CHOOSE_24_SAMPLES)
        self.RADIOBUTTON_GROUP_CHOOSE_SAMPLES.addButton(self.RADIOBUTTON_CHOOSE_SAMPLE_SHEET)

        #set up button to show info-text for sample info-sheet upload -> uses function "info"; only active when using 96-sample sheet input
        self.PUSHBUTTON_INFO_MSG = QtWidgets.QPushButton(self)
        self.PUSHBUTTON_INFO_MSG.setText('info')
        self.PUSHBUTTON_INFO_MSG.setDisabled(True)
        self.PUSHBUTTON_INFO_MSG.move(365, 350)
        self.PUSHBUTTON_INFO_MSG.setHidden(True)
        self.PUSHBUTTON_INFO_MSG.clicked.connect(self.info)

        #set up upload button for user barcode-file
        self.PUSHBUTTON_UPLOAD_SAMPLE_INFO = QtWidgets.QPushButton(self)
        self.PUSHBUTTON_UPLOAD_SAMPLE_INFO.setText('upload sample information')
        self.PUSHBUTTON_UPLOAD_SAMPLE_INFO.adjustSize()
        self.PUSHBUTTON_UPLOAD_SAMPLE_INFO.setDisabled(True)
        self.PUSHBUTTON_UPLOAD_SAMPLE_INFO.move(540,350)
        self.PUSHBUTTON_UPLOAD_SAMPLE_INFO.clicked.connect(self.upload_sample_info)
        #show tooltip with help message while mouse hovers on button
        self.PUSHBUTTON_UPLOAD_SAMPLE_INFO.setToolTip('Click info to activate. Upload your 96-samples')
        self.setStyleSheet("""QToolTip { 
                           background-color: black; 
                           color: white; 
                           border: black solid 1px
                           }""")

        self.PUSHBUTTON_UPLOAD_SAMPLE_INFO.setHidden(True)

        #set up input fields for user, ip-adresse and pathes on server and to upload dir
        self.INPUT_USERNAME = QtWidgets.QLineEdit(self)
        self.INPUT_USERNAME.move(10, 400)
        self.INPUT_USERNAME.setPlaceholderText('username')

        self.INPUT_IP_ADDRESSE = QtWidgets.QLineEdit(self)
        self.INPUT_IP_ADDRESSE.move(125, 400)
        self.INPUT_IP_ADDRESSE.setPlaceholderText('ip-adress')
        self.INPUT_IP_ADDRESSE.resize(120, 30)

        self.LABEL_AT = QtWidgets.QLabel(self)
        self.LABEL_AT.move(112, 407)
        self.LABEL_AT.setText('@')
        self.LABEL_AT.adjustSize()

        self.INPUT_SERVER_PATH = QtWidgets.QLineEdit(self)
        self.INPUT_SERVER_PATH.move(10, 440)
        self.INPUT_SERVER_PATH.setPlaceholderText('/path/on/server')
        self.INPUT_SERVER_PATH.resize(290, 30)

        self.INPUT_UPLOAD_DIR_PATH = QtWidgets.QLineEdit(self)
        self.INPUT_UPLOAD_DIR_PATH.move(10, 500)
        self.INPUT_UPLOAD_DIR_PATH.setPlaceholderText('/path/to/dir')
        self.INPUT_UPLOAD_DIR_PATH.resize(290, 30)

        #set up push button to test server connection
        self.PSUHBUTTON_TEST_CONNECTION = QtWidgets.QPushButton(self)
        self.PSUHBUTTON_TEST_CONNECTION.move(320, 440)
        self.PSUHBUTTON_TEST_CONNECTION.setText('test connection')
        self.PSUHBUTTON_TEST_CONNECTION.clicked.connect(self.test_upload)

        #set up input field for additional info
        self.INPUT_ADDITIONAL_INFO = QtWidgets.QTextEdit(self)
        self.INPUT_ADDITIONAL_INFO.setPlaceholderText(f"Additional information:\tThis info will be uploaded to the server with run_info.txt")
        self.INPUT_ADDITIONAL_INFO.setGeometry(430, 400, 365, 195)

        #set up push button to check data
        self.PUSHBUTTON_CHECK_DATA = QtWidgets.QPushButton(self)
        self.PUSHBUTTON_CHECK_DATA.setText('check data')
        self.PUSHBUTTON_CHECK_DATA.move(40, 350)
        self.PUSHBUTTON_CHECK_DATA.setWhatsThis('check your data')
        self.PUSHBUTTON_CHECK_DATA.clicked.connect(self.passInformation)   #upon clicking call function to open another window

        #set up push button to choose upload dir
        self.PUSHBUTTON_CHOOSE_UPLOAD_DIR = QtWidgets.QPushButton(self)
        self.PUSHBUTTON_CHOOSE_UPLOAD_DIR.setText('choose dir')
        self.PUSHBUTTON_CHOOSE_UPLOAD_DIR.move(320, 500)
        self.PUSHBUTTON_CHOOSE_UPLOAD_DIR.clicked.connect(self.choose_upload_dir)

        #set up push button to upload data to server (with tooltip)
        self.PUSHBUTTON_UPLOAD_TO_SERVER = QtWidgets.QPushButton(self)
        self.PUSHBUTTON_UPLOAD_TO_SERVER.setText('Upload')
        self.PUSHBUTTON_UPLOAD_TO_SERVER.move(40, 560)
        self.PUSHBUTTON_UPLOAD_TO_SERVER.setToolTip('check data before upload')
        self.setStyleSheet("""QToolTip { 
                           background-color: black; 
                           color: white; 
                           border: black solid 1px
                           }""")
        self.PUSHBUTTON_UPLOAD_TO_SERVER.clicked.connect(self.upload)

        #set up hidden, empty label to choose amount of samples in upload_to_server function
        self.LABEL_BARCODE_BUTTON_STATUS = QtWidgets.QLabel(self)
        self.LABEL_BARCODE_BUTTON_STATUS.setText('no')
        self.LABEL_BARCODE_BUTTON_STATUS.setHidden(True)

        """self.label_image = QtWidgets.QLabel(self)
        self.label_image.move(300, 140)
        self.label
        self.image = QtGui.QPixmap('image.png')
        self.label_image.setPixmap(self.image)"""

        #set up hidden table
        self.WIDGET_MOCK_EXCEL_TABLE = QtWidgets.QTableWidget(self)
        self.WIDGET_MOCK_EXCEL_TABLE.move(250, 60)
        self.WIDGET_MOCK_EXCEL_TABLE.setHidden(True)
        self.WIDGET_MOCK_EXCEL_TABLE.setRowCount(6) #row count
        self.WIDGET_MOCK_EXCEL_TABLE.setColumnCount(2)  #column count

        #insert values in table [row, column, value]
        self.WIDGET_MOCK_EXCEL_TABLE.setItem(0, 0, QtWidgets.QTableWidgetItem("barcode"))
        self.WIDGET_MOCK_EXCEL_TABLE.setItem(0, 1, QtWidgets.QTableWidgetItem("sample_id"))
        self.WIDGET_MOCK_EXCEL_TABLE.setItem(1, 0, QtWidgets.QTableWidgetItem("1"))
        self.WIDGET_MOCK_EXCEL_TABLE.setItem(1, 1, QtWidgets.QTableWidgetItem("sample_1"))
        self.WIDGET_MOCK_EXCEL_TABLE.setItem(2, 0, QtWidgets.QTableWidgetItem("2"))
        self.WIDGET_MOCK_EXCEL_TABLE.setItem(2, 1, QtWidgets.QTableWidgetItem("sample_2"))
        self.WIDGET_MOCK_EXCEL_TABLE.setItem(3, 0, QtWidgets.QTableWidgetItem("3"))
        self.WIDGET_MOCK_EXCEL_TABLE.setItem(3, 1, QtWidgets.QTableWidgetItem("sample_3"))
        self.WIDGET_MOCK_EXCEL_TABLE.setItem(4, 0, QtWidgets.QTableWidgetItem("4"))
        self.WIDGET_MOCK_EXCEL_TABLE.setItem(4, 1, QtWidgets.QTableWidgetItem("sample_4"))
        self.WIDGET_MOCK_EXCEL_TABLE.setItem(5, 0, QtWidgets.QTableWidgetItem("6"))
        self.WIDGET_MOCK_EXCEL_TABLE.setItem(5, 1, QtWidgets.QTableWidgetItem("sample_6"))
        self.WIDGET_MOCK_EXCEL_TABLE.setItem(6, 0, QtWidgets.QTableWidgetItem("7"))
        self.WIDGET_MOCK_EXCEL_TABLE.setItem(6, 1, QtWidgets.QTableWidgetItem("sample_7"))

        #define table outlines and trigger on edit
        self.WIDGET_MOCK_EXCEL_TABLE.setMaximumWidth(215)
        self.WIDGET_MOCK_EXCEL_TABLE.setMinimumWidth(215)
        self.WIDGET_MOCK_EXCEL_TABLE.setMaximumHeight(250)
        self.WIDGET_MOCK_EXCEL_TABLE.setMinimumHeight(250)
        self.WIDGET_MOCK_EXCEL_TABLE.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        #table cant be changed
        self.WIDGET_MOCK_EXCEL_TABLE.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.WIDGET_MOCK_EXCEL_TABLE.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        #set up labels for table
        self.LABEL_MOCK_EXCEL_TABLE = QtWidgets.QLabel(self)
        self.LABEL_MOCK_EXCEL_TABLE.setText("xlsx example:")
        self.LABEL_MOCK_EXCEL_TABLE.move(250,30)
        self.LABEL_MOCK_EXCEL_TABLE.setHidden(True)
        self.LABEL_MOCK_EXCEL_TABLE.setFont(QtGui.QFont("arial", 15))
        self.LABEL_MOCK_EXCEL_TABLE.adjustSize()

        #set up input field and label for csv example
        self.INPUT_MOCK_CSV = QtWidgets.QTextEdit(self)   #little edit field to add additional info
        self.INPUT_MOCK_CSV.setPlaceholderText(f"barcode,sample_id\n1,sample_1\n2,sample_2\n3,sample_3\n4,sample4\n5,sample_5\n6,sample_6")
        self.INPUT_MOCK_CSV.setGeometry(540, 60, 225, 250)
        self.INPUT_MOCK_CSV.setHidden(True)
        self.LABEL_MOCK_CSV = QtWidgets.QLabel(self)
        self.LABEL_MOCK_CSV.setText("csv example:")
        self.LABEL_MOCK_CSV.move(540, 30)
        self.LABEL_MOCK_CSV.setHidden(True)
        self.LABEL_MOCK_CSV.setFont(QtGui.QFont("arial", 15))
        self.LABEL_MOCK_CSV.adjustSize()

        #set up checkbox to exclud fast5/pod5 files from upload
        self.EXCLUDE_FAST5_FILES = QtWidgets.QCheckBox('exclude fast5/pod5 files', self)
        self.EXCLUDE_FAST5_FILES.move(150, 565)
        self.EXCLUDE_FAST5_FILES.adjustSize()

        # check if there is a user_info.txt if not no abortion -> file is created in function "test_upload"
        try:    #test if command can be executed else exceptions according to errors
            USER_PRE_INFO_FILE = open(self.NORSE_USER_INFO_PATH, 'r')    #open file in read-mode
            USER_PRE_INFO_LIST = USER_PRE_INFO_FILE.read().splitlines()  #read file splitting into list by lines
            
            #put username, ip-adresse and server-path into according fields in the GUI
            self.INPUT_USERNAME.setText(USER_PRE_INFO_LIST[0])
            self.INPUT_IP_ADDRESSE.setText(USER_PRE_INFO_LIST[1])
            self.INPUT_SERVER_PATH.setText(USER_PRE_INFO_LIST[2])
        
            USER_PRE_INFO_FILE.close()  #close file
            #self.LABEL_TEST_UPLOAD_VARIABLE.setText('true')

        #capture exceptions
        except IndexError:
            print('index error')
        except FileNotFoundError:
            print('file not found')


    def choose_upload_dir(self):   #def directory select function for upload dir (pyqt5 build-in function)
        UPLOAD_DIR_PATH = QFileDialog().getExistingDirectory(self, 'Select an  directory')  #set up dialg field
        self.INPUT_UPLOAD_DIR_PATH.setText(UPLOAD_DIR_PATH)  #put upload dir path into according field after selection


    def upload(self, state):    #def function to upload files and create run_info.txt
        #def variables using inputs from the according GUI fields
        ADDITIONAL_INFO = self.INPUT_ADDITIONAL_INFO.toPlainText()
        BARCODE_KIT = self.INPUT_BARCODE_KIT.currentText()
        BARCODE_BUTTON_STATUS = self.LABEL_BARCODE_BUTTON_STATUS.text()
        DATE = datetime.today().strftime('%Y-%m-%d-%H%M%S')
        EXCLUDE_FAST5_FILES_STATUS = self.EXCLUDE_FAST5_FILES.isChecked()
        FLOWCELL_TYPE = self.INPUT_FLOWCELL_TYPE.currentText()
        IP_ADDRESSE = self.INPUT_IP_ADDRESSE.text()
        PASSWORD = self.INPUT_PASSWORD.text()
        SERVER_PATH = self.INPUT_SERVER_PATH.text()
        SEQ_KIT = self.INPUT_SEQUENCING_KIT.currentText()
        UPLOAD_DIR_PATH = self.INPUT_UPLOAD_DIR_PATH.text()
        USERNAME = self.INPUT_USERNAME.text()

        #set up message window to capture empty variables from above
        MSG_UPLOAD_ERROR = QMessageBox()
        MSG_UPLOAD_ERROR.setWindowTitle("user info")
        if USERNAME == "":
            MSG_UPLOAD_ERROR.setText("username is empty")
            x = MSG_UPLOAD_ERROR.exec_()
            return 13
        if IP_ADDRESSE == "":
            MSG_UPLOAD_ERROR.setText("ip-address is empty")
            x = MSG_UPLOAD_ERROR.exec_()
            return 14
        if PASSWORD == "":
            MSG_UPLOAD_ERROR.setText("password is empty")
            x = MSG_UPLOAD_ERROR.exec_()
            return 15
        if SERVER_PATH == "":
            MSG_UPLOAD_ERROR.setText("\"/path/on/server\" (directory on server) is empty")
            x = MSG_UPLOAD_ERROR.exec_()
            return 16
        if UPLOAD_DIR_PATH == "":
            MSG_UPLOAD_ERROR.setText("\"/path/to/dir\" (upload directory) is empty")
            x = MSG_UPLOAD_ERROR.exec_()
            return 17

        #use individual dir name if user input exists
        if self.INPUT_DIR_NAME.text():
            UPLOAD_DIR_NAME = self.INPUT_DIR_NAME.text()
        else:
            UPLOAD_DIR_NAME = os.path.basename(os.path.normpath(UPLOAD_DIR_PATH))
        
        NEW_UPLOAD_DIR_NAME = DATE + '_' + UPLOAD_DIR_NAME
        print(NEW_UPLOAD_DIR_NAME)

        #create run_info.txt
        run_info_file_path = os.path.join(UPLOAD_DIR_PATH, "run_info.txt")    
        RUN_INFO_FILE = open(run_info_file_path, "w")

        #write general information to run_info.txt
        RUN_INFO_FILE.write(f'Automatically generated by norse (version: {VERSION})\n')
        RUN_INFO_FILE.write(f'##Kit:\t{SEQ_KIT}\n')
        RUN_INFO_FILE.write(f'##Barcodekit:\t{BARCODE_KIT}\n')
        RUN_INFO_FILE.write(f'##Flowcell:\t{FLOWCELL_TYPE}\n')
        RUN_INFO_FILE.write(f'##Run name:\t{NEW_UPLOAD_DIR_NAME}\n')
        
        #write barcode-sampleIDs to run_info.txt
        RUN_INFO_FILE.write("Barcode\tSample-name\n")
        
        #no barcodes -> single sample
        if BARCODE_BUTTON_STATUS == 'no':
            LINEEDIT01 = self.LINEEDIT1.text()
            RUN_INFO_FILE.write(f'Sample\t{LINEEDIT01}')

        #barcodes 1-12 (active if "yes" or "24" selected)
        elif BARCODE_BUTTON_STATUS in ['yes', '24']:
            #def variables getting sampleID from according barcode field in GUI
            LINEEDIT01 = self.LINEEDIT1.text()
            LINEEDIT02 = self.LINEEDIT2.text()
            LINEEDIT03 = self.LINEEDIT3.text()
            LINEEDIT04 = self.LINEEDIT4.text()
            LINEEDIT05 = self.LINEEDIT5.text()
            LINEEDIT06 = self.LINEEDIT6.text()
            LINEEDIT07 = self.LINEEDIT7.text()
            LINEEDIT08 = self.LINEEDIT8.text()
            LINEEDIT09 = self.LINEEDIT9.text()
            LINEEDIT10 = self.LINEEDIT10.text()
            LINEEDIT11 = self.LINEEDIT11.text()
            LINEEDIT12 = self.LINEEDIT12.text()
            
            #add all 12 variables to list
            BARCODE_SAMPLE_LIST = [LINEEDIT01,LINEEDIT02,LINEEDIT03,LINEEDIT04,LINEEDIT05,LINEEDIT06,LINEEDIT07,LINEEDIT08,
            LINEEDIT09,LINEEDIT10,LINEEDIT11,LINEEDIT12]

            #barcodes 13-24 (active if "24" selected)
            if BARCODE_BUTTON_STATUS == '24':
                LINEEDIT13 = self.LINEEDIT13.text()
                LINEEDIT14 = self.LINEEDIT14.text()
                LINEEDIT15 = self.LINEEDIT15.text()
                LINEEDIT16 = self.LINEEDIT16.text()
                LINEEDIT17 = self.LINEEDIT17.text()
                LINEEDIT18 = self.LINEEDIT18.text()
                LINEEDIT19 = self.LINEEDIT19.text()
                LINEEDIT20 = self.LINEEDIT20.text()
                LINEEDIT21 = self.LINEEDIT21.text()
                LINEEDIT22 = self.LINEEDIT22.text()
                LINEEDIT23 = self.LINEEDIT23.text()
                LINEEDIT24 = self.LINEEDIT24.text()

                #extend list by additional sampleIDs for barcodes 13-24
                BARCODE_SAMPLE_LIST.extend([LINEEDIT13,LINEEDIT14,LINEEDIT15,LINEEDIT16,LINEEDIT17,LINEEDIT18,LINEEDIT19,LINEEDIT20,
                LINEEDIT21,LINEEDIT22,LINEEDIT23,LINEEDIT24])
            
            #write barcodes + sampleIDs to run_info.txt
            for INDEX in range(len(BARCODE_SAMPLE_LIST)):
                if INDEX < 9:
                    RUN_INFO_FILE.write(f'barcode0{str(INDEX + 1)}\t{BARCODE_SAMPLE_LIST[INDEX]}\n')
                else:
                    RUN_INFO_FILE.write(f'barcode{str(INDEX + 1)}\t{BARCODE_SAMPLE_LIST[INDEX]}\n')

        #up to 96 barcodes via user input-file
        elif BARCODE_BUTTON_STATUS == "96":
            #check file type and read into panda dataframe
            if self.FILE_1 == "csv":
                BARCODE_SAMPLE_DF = pd.read_csv(self.UPLOAD_SAMPLE_PATH, sep = ',', header=None)
            elif self.FILE_1 == "tsv":
                BARCODE_SAMPLE_DF = pd.read_csv(self.UPLOAD_SAMPLE_PATH, sep = "\t", header=None)
            elif self.FILE_1 == "xlsx":
                BARCODE_SAMPLE_DF = pd.read_excel(self.UPLOAD_SAMPLE_PATH, header=None)

            #read dataframe
            ROW = 0
            BARCODE_FILE_DF_LENGTH = len(BARCODE_SAMPLE_DF)
            while True:
                if BARCODE_SAMPLE_DF.iloc[ROW, 0] == "barcode":   #detect header
                    ROW = ROW + 1   #set begin to row after header
                    for ROWS in range(ROW, BARCODE_FILE_DF_LENGTH):  #loop over all rows following the header
                        if ROWS < 10:
                            RUN_INFO_FILE.write(f'barcode0{str(BARCODE_SAMPLE_DF.iloc[ROWS, 0])}\t{str(BARCODE_SAMPLE_DF.iloc[ROWS, 1])}\n')
                        else:
                            RUN_INFO_FILE.write(f'barcode{str(BARCODE_SAMPLE_DF.iloc[ROWS, 0])}\t{str(BARCODE_SAMPLE_DF.iloc[ROWS, 1])}\n')
                    break   #end while loop
                else:
                    ROW = ROW + 1   #increase ROW variable -> go to next row 
                    if ROW == BARCODE_FILE_DF_LENGTH:    #check if actual row is last row in file
                        ROW = 0
                        break   #add here a sys.exit to tell user he has to rename column???

        #write additional info to run_info.txt
        RUN_INFO_FILE.write(f'\n##Additional info\n{ADDITIONAL_INFO}\n')

        #close run_info.txt
        RUN_INFO_FILE.close()

        #check if rsync is avaible if yes then command (which rsync oder rsync -v)
        #os.system(f'rsync --rsync-path="/bin/rsync" -acr --remove-source-files "{upload_dir_path}" "~/Desktop/test_server/{new_upload_dir_name}"')
        #else scp

        port = 22
        cmd = 'which rsync'
        cmd2 = 'echo $?'

        #connect and upload to server -> if failure occurs error is printed. Connection is tested separately in func "test_upload"
        try:
            #set up messsage window (pop-up)
            MSG_UPLOAD_STARTED = QMessageBox()
            MSG_UPLOAD_STARTED.setWindowTitle("upload started")
            MSG_UPLOAD_STARTED.setText("Upload started")
            x = MSG_UPLOAD_STARTED.exec()
            MSG_UPLOAD_STATUS = QMessageBox()
            MSG_UPLOAD_STATUS.setWindowTitle("upload")

            ###deactivated rsync check for now due to server-sided permission issues related to this 
            # ssh = paramiko.SSHClient()
            # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # ssh.connect(ip ,port ,username ,password, timeout=10)
            # stdin,stdout,stderr = ssh.exec_command(cmd) 
            # time.sleep(5)
            # outlines = stdout.readlines()
            # resp = ''.join(outlines)
            # rsync_var = resp
            # rsync_var = rsync_var.strip()

            # ssh2 = paramiko.SSHClient()
            # ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # ssh2.connect(ip ,port ,username ,password, timeout=10)
            # stdin,stdout,stderr = ssh2.exec_command("which rsync \n echo $?") 
            # time.sleep(5)
            # outlines2 = stdout.readlines()
            # exit_code = outlines2[1]
            # exit_code = exit_code.strip()
            exit_code = "1" #hardcoded this to always use the rsync option for the moment
            
            if exit_code == "0":
                if EXCLUDE_FAST5_FILES_STATUS == False:
                    EXCLUDE_FAST5 = ''
                else:
                    EXCLUDE_FAST5 = '--exclude "*.fast5" --exclude "*.pod5"'
                
                #os.system('scp -r ' + upload_dir_path + username + "@" +
                    #   ip + ":" + path_on_server + "/" + new_upload_dir_name)
                SCP_EXIT_CODE = os.system(f'scp -r {UPLOAD_DIR_PATH} {USERNAME}@{IP_ADDRESSE}:"{SERVER_PATH}"/"{NEW_UPLOAD_DIR_NAME}"')
                if SCP_EXIT_CODE != 0:
                    MSG_UPLOAD_STATUS.setText("upload failed")
                    x = MSG_UPLOAD_STATUS.exec_()
                else:
                    MSG_UPLOAD_STATUS.setText("upload complete")
                    x = MSG_UPLOAD_STATUS.exec_()

            #rsync upload
            else:
                #def variable to insert flag depending on fast5 exclusion yes/no
                if EXCLUDE_FAST5_FILES_STATUS == False:
                    EXCLUDE_FAST5 = ''
                else:
                    EXCLUDE_FAST5 = '--exclude "*.fast5" --exclude "*.pod5"'
                
                RSYNC_EXIT_CODE = os.system(f'sshpass -p {PASSWORD} rsync {EXCLUDE_FAST5} -acrv --remove-source-files "{UPLOAD_DIR_PATH}" {USERNAME}@{IP_ADDRESSE}:"{SERVER_PATH}"/"{NEW_UPLOAD_DIR_NAME}"')
                
                #check exit code and display pop-up message according to result
                if RSYNC_EXIT_CODE != 0:
                    MSG_UPLOAD_STATUS.setText("upload failed")
                    x = MSG_UPLOAD_STATUS.exec_()
                else:
                    MSG_UPLOAD_STATUS.setText("upload complete")
                    x = MSG_UPLOAD_STATUS.exec_()                      
                    #sys.exit(0)

        #capture according errors
        except paramiko.AuthenticationException:
            print('connection error')
        except socket.timeout:
            print('connection error')
        

    def sequencing_kit_changed(self):   #def function to check input for seq-kit field in GUI
        #open file with all available seq-kit options and read line-wise into list
        with open('/norse/data/sequencing_kit_data.txt') as file:
            SEQUENCING_KIT_LIST = [line.rstrip() for line in file]

        #def variables
        SEQUENCING_KIT_INPUT = self.INPUT_SEQUENCING_KIT.currentText()
        SEQKIT = 0

        #check if field is not empty (str length > 0)
        if len(SEQUENCING_KIT_INPUT) > 0:
            #compare input to seq-kit list entries and break if match
            for ELEMENT in SEQUENCING_KIT_LIST:
                if ELEMENT == SEQUENCING_KIT_INPUT:
                    SEQKIT = 1
                    break

            #if input does not match seq-kit list entries inform user via pop-up message and reset input-field to first seq-kit list entry
            if SEQKIT == 0:
                MSG_SEQUENCING_KIT_INVALID = QMessageBox()
                MSG_SEQUENCING_KIT_INVALID.setIcon(QMessageBox.Critical)
                MSG_SEQUENCING_KIT_INVALID.setWindowTitle("Sequencing-Kit input")
                MSG_SEQUENCING_KIT_INVALID.setText(f"Something is wrong with your input!\nResetting Box-value.")
                x = MSG_SEQUENCING_KIT_INVALID.exec_()  # this will show our messagebox
                self.INPUT_SEQUENCING_KIT.setEditText(f"{SEQUENCING_KIT_LIST[0]}")

    def barcode_kit_changed(self):  #def function to check input for barcode-kit field in GUI (analog to "sequencing_kit_changed" function)
        with open('/norse/data/barcoding_kit_data.txt') as file:
            BARCODE_KIT_LIST = [LINE.rstrip() for LINE in file]

        BARCODE_KIT_INPUT = self.INPUT_BARCODE_KIT.currentText()
        BARCODEKIT = 0

        if len(BARCODE_KIT_INPUT) > 0:
            for ELEMENT in BARCODE_KIT_LIST:
                if ELEMENT == BARCODE_KIT_INPUT:
                    BARCODEKIT = 1
                    break
            
            if BARCODEKIT == 0:
                MSG_BARCODE_KIT_INVALID = QMessageBox()
                MSG_BARCODE_KIT_INVALID.setIcon(QMessageBox.Critical)
                MSG_BARCODE_KIT_INVALID.setWindowTitle("Barcode-kit input")
                MSG_BARCODE_KIT_INVALID.setText(f"Something is wrong with your input!\nResetting Box-value.")
                x = MSG_BARCODE_KIT_INVALID.exec_()  # this will show our messagebox
                self.INPUT_BARCODE_KIT.setEditText(f"{BARCODE_KIT_LIST[0]}")


    def flowcell_changed(self): #def function to check input for flowcell field in GUI (analog to "sequencing_kit_changed" function)
        with open('/norse/data/flowcell_data.txt') as file:
            FLOWCELL_TYPE_LIST = [line.rstrip() for line in file]

        FLOWCELL_INPUT = self.INPUT_FLOWCELL_TYPE.currentText()
        FLOWCELL = 0

        if len(FLOWCELL_INPUT) > 0:
            for ELEMENT in FLOWCELL_TYPE_LIST:
                if ELEMENT == FLOWCELL_INPUT:
                    FLOWCELL = 1
                    break
            
            if FLOWCELL == 0:
                MSG_FLOWCELL_TYPE_INVALID = QMessageBox()
                MSG_FLOWCELL_TYPE_INVALID.setIcon(QMessageBox.Critical)
                MSG_FLOWCELL_TYPE_INVALID.setWindowTitle("Flowcell input")
                MSG_FLOWCELL_TYPE_INVALID.setText(f"Something is wrong with your input!\nResetting Box-value.")
                x = MSG_FLOWCELL_TYPE_INVALID.exec_()  # this will show our messagebox
                self.INPUT_FLOWCELL_TYPE.setEditText(f"{FLOWCELL_TYPE_LIST[0]}")


    def test_upload(self):  #def function to test connection to server and add info to user_info.txt
        USERNAME = self.INPUT_USERNAME.text()
        IP_ADDRESSE = self.INPUT_IP_ADDRESSE.text()
        PASSWORD = self.INPUT_PASSWORD.text()
        SERVER_PATH = self.INPUT_SERVER_PATH.text()

        #write user-info (username, ip-addresse, path-on-server) to file -> file is loaded when Norse is opened, prefilling the according fields
        USER_INFO = open(self.NORSE_USER_INFO_PATH, "w+")   #open new file with write acess
        USER_INFO.truncate(0)   #delete file content by "resizing" it to 0 bytes
        USER_INFO.write(f'{USERNAME}\n{IP_ADDRESSE}\n{SERVER_PATH}')    #write variables to file
        USER_INFO.close()   #close file

        #set-up msg
        TEST_UPLOAD_MSG = QMessageBox()
        TEST_UPLOAD_MSG.setWindowTitle("test connection")

        #execute rsync-dryrun to simulate upload and capture exit code
        RSYNC_TEST_EXIT_CODE = os.system(f'sshpass -p {PASSWORD} rsync --dry-run -acrq "norse/data/run_info.txt" {USERNAME}@{IP_ADDRESSE}:"{SERVER_PATH}"/ >/dev/null 2>&1')
  
        if RSYNC_TEST_EXIT_CODE == 0:
            TEST_UPLOAD_MSG.setText("Connected successfull")
            TEST_UPLOAD_MSG.setIcon(QMessageBox.Information)
        elif RSYNC_TEST_EXIT_CODE == 256:
            TEST_UPLOAD_MSG.setText("Error: Password field is empty!")
            TEST_UPLOAD_MSG.setIcon(QMessageBox.Critical)
        elif RSYNC_TEST_EXIT_CODE == 1280:
            TEST_UPLOAD_MSG.setText("Error: Wrong username or password!")
            TEST_UPLOAD_MSG.setIcon(QMessageBox.Critical)
        elif RSYNC_TEST_EXIT_CODE == 3072:
            TEST_UPLOAD_MSG.setText("Error: Empty or wrong server-path")    #error also occurs if server path without necessary access rights is given
            TEST_UPLOAD_MSG.setIcon(QMessageBox.Critical)
        elif RSYNC_TEST_EXIT_CODE == 65280:
            TEST_UPLOAD_MSG.setText("Error: Empty or wrong IP-addresse!")
            TEST_UPLOAD_MSG.setIcon(QMessageBox.Critical)
        x = TEST_UPLOAD_MSG.exec_()


    def radiobutton_no(self):  #button: no barcodes
        #hide for this barcode-option unnecessary sample-id fields in Window2 (check-data window)
        self.WINDOW2.hide_and_show(2,24,True)

        self.LABEL_BARCODE_BUTTON_STATUS.setText('no')  #set text for label
        globs, locs = globals(), locals()   #get global and local variables
        
        #hide all Label- and Input-fields in the MainWindow
        [exec(f'self.{LABEL_NAME}.setHidden(True)', globs,locs) for LABEL_NAME in self.LABEL_NAME_LIST_MAIN[(0):24]]
        [exec(f'self.{INPUT_NAME}.setHidden(True)', globs,locs) for INPUT_NAME in self.INPUT_NAME_LIST_MAIN[(0):24]]

        #show the for this barcode-option necessary LABEL- and INPUT-fields in the MainWindow
        self.LABEL1.setHidden(False)
        self.LINEEDIT1.setHidden(False)

        #hide and disable buttons and elements that are not shown when this barcoding-option is chosen
        self.PUSHBUTTON_UPLOAD_SAMPLE_INFO.setHidden(True)
        self.PUSHBUTTON_UPLOAD_SAMPLE_INFO.setDisabled(True)
        self.PUSHBUTTON_INFO_MSG.setHidden(True)
        self.PUSHBUTTON_INFO_MSG.setDisabled(True)
        self.WIDGET_MOCK_EXCEL_TABLE.setHidden(True)
        self.LABEL_MOCK_EXCEL_TABLE.setHidden(True)
        self.INPUT_MOCK_CSV.setHidden(True)
        self.LABEL_MOCK_CSV.setHidden(True)
   

    def radiobutton_yes(self): #button: 1-12 samples with barcodes; analog to function "radiobutton_no"
        self.WINDOW2.hide_and_show(1,12,False)
        self.WINDOW2.hide_and_show(13,24,True)
        self.LABEL_BARCODE_BUTTON_STATUS.setText('yes')
        
        globs, locs = globals(), locals()
        [exec(f'self.{LABEL_NAME}.setHidden(False)', globs, locs) for LABEL_NAME in self.LABEL_NAME_LIST_MAIN[(0):12]]
        [exec(f'self.{INPUT_NAME}.setHidden(False)', globs, locs) for INPUT_NAME in self.INPUT_NAME_LIST_MAIN[(0):12]]
        
        [exec(f'self.{LABEL_NAME}.setHidden(True)', globs, locs) for LABEL_NAME in self.LABEL_NAME_LIST_MAIN[(12):24]]
        [exec(f'self.{INPUT_NAME}.setHidden(True)', globs, locs) for INPUT_NAME in self.INPUT_NAME_LIST_MAIN[(12):24]]

        self.PUSHBUTTON_UPLOAD_SAMPLE_INFO.setHidden(True)
        self.PUSHBUTTON_UPLOAD_SAMPLE_INFO.setDisabled(True)
        self.PUSHBUTTON_INFO_MSG.setHidden(True)
        self.PUSHBUTTON_INFO_MSG.setDisabled(True)
        self.WIDGET_MOCK_EXCEL_TABLE.setHidden(True)
        self.LABEL_MOCK_EXCEL_TABLE.setHidden(True)
        self.INPUT_MOCK_CSV.setHidden(True)
        self.LABEL_MOCK_CSV.setHidden(True)


    def radiobutton_24(self):   #button: 1-24 samples with barcodes; analog to function "radiobutton_no"
        self.LABEL_BARCODE_BUTTON_STATUS.setText('24')

        globs, locs = globals(), locals()
        [exec(f'self.{LABEL_NAME}.setHidden(False)', globs, locs) for LABEL_NAME in self.LABEL_NAME_LIST_MAIN[(0):24]]
        [exec(f'self.{INPUT_NAME}.setHidden(False)', globs, locs) for INPUT_NAME in self.INPUT_NAME_LIST_MAIN[(0):24]]

        self.WINDOW2.hide_and_show(1,24,False)

        self.PUSHBUTTON_UPLOAD_SAMPLE_INFO.setHidden(True)
        self.PUSHBUTTON_UPLOAD_SAMPLE_INFO.setDisabled(True)
        self.PUSHBUTTON_INFO_MSG.setHidden(True)
        self.PUSHBUTTON_INFO_MSG.setDisabled(True)
        self.WIDGET_MOCK_EXCEL_TABLE.setHidden(True)
        self.LABEL_MOCK_EXCEL_TABLE.setHidden(True)
        self.INPUT_MOCK_CSV.setHidden(True)
        self.LABEL_MOCK_CSV.setHidden(True)


    def radiobutton_96(self):   #button: up to 96 samples with barcodes; analog to function "radiobutton_no"
            self.LABEL_BARCODE_BUTTON_STATUS.setText('96')
            self.PUSHBUTTON_UPLOAD_SAMPLE_INFO.setHidden(False)
            self.PUSHBUTTON_UPLOAD_SAMPLE_INFO.setDisabled(False)
            self.PUSHBUTTON_INFO_MSG.setHidden(False)
            self.PUSHBUTTON_INFO_MSG.setDisabled(False)
            self.WIDGET_MOCK_EXCEL_TABLE.setHidden(False)
            self.LABEL_MOCK_EXCEL_TABLE.setHidden(False)
            self.INPUT_MOCK_CSV.setHidden(False)
            self.LABEL_MOCK_CSV.setHidden(False)
            self.WINDOW2.hide_and_show(1,24,True)

            globs, locs = globals(), locals()
            [exec(f'self.{LABEL_NAME}.setHidden(True)', globs, locs) for LABEL_NAME in self.LABEL_NAME_LIST_MAIN[(0):24]]
            [exec(f'self.{INPUT_NAME}.setHidden(True)', globs, locs) for INPUT_NAME in self.INPUT_NAME_LIST_MAIN[(0):24]]
            
            self.WINDOW2.hide()
    

    def passInformation(self):    #function to give infos from Mainwindow to Window2 (WINDOW2_libraries.py) to display there
        #writes current value of the variable to the variable in Window2
        self.WINDOW2.INPUT_FLOWCELL_TYPE.setText(self.INPUT_FLOWCELL_TYPE.currentText())
        self.WINDOW2.INPUT_SEQ_KIT.setText(self.INPUT_SEQUENCING_KIT.currentText())
        self.WINDOW2.INPUT_BARCODE_KIT.setText(self.INPUT_BARCODE_KIT.currentText())
        self.WINDOW2.INPUT1.setText(self.LINEEDIT1.text())
        self.WINDOW2.INPUT2.setText(self.LINEEDIT2.text())
        self.WINDOW2.INPUT3.setText(self.LINEEDIT3.text())
        self.WINDOW2.INPUT4.setText(self.LINEEDIT4.text())
        self.WINDOW2.INPUT5.setText(self.LINEEDIT5.text())
        self.WINDOW2.INPUT6.setText(self.LINEEDIT6.text())
        self.WINDOW2.INPUT7.setText(self.LINEEDIT7.text())
        self.WINDOW2.INPUT8.setText(self.LINEEDIT8.text())
        self.WINDOW2.INPUT9.setText(self.LINEEDIT9.text())
        self.WINDOW2.INPUT10.setText(self.LINEEDIT10.text())
        self.WINDOW2.INPUT11.setText(self.LINEEDIT11.text())
        self.WINDOW2.INPUT12.setText(self.LINEEDIT12.text())
        self.WINDOW2.INPUT13.setText(self.LINEEDIT13.text())
        self.WINDOW2.INPUT14.setText(self.LINEEDIT14.text())
        self.WINDOW2.INPUT15.setText(self.LINEEDIT15.text())
        self.WINDOW2.INPUT16.setText(self.LINEEDIT16.text())
        self.WINDOW2.INPUT17.setText(self.LINEEDIT17.text())
        self.WINDOW2.INPUT18.setText(self.LINEEDIT18.text())
        self.WINDOW2.INPUT19.setText(self.LINEEDIT19.text())
        self.WINDOW2.INPUT20.setText(self.LINEEDIT20.text())
        self.WINDOW2.INPUT21.setText(self.LINEEDIT21.text())
        self.WINDOW2.INPUT22.setText(self.LINEEDIT22.text())
        self.WINDOW2.INPUT23.setText(self.LINEEDIT23.text())
        self.WINDOW2.INPUT24.setText(self.LINEEDIT24.text())

        #show Window2
        self.WINDOW2.displayInfo()


    def password_hide_show(self, STATE):   #function to show/hide password in according field based on status of the tick-box
        if STATE == QtCore.Qt.Checked:
            self.INPUT_PASSWORD.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.INPUT_PASSWORD.setEchoMode(QtWidgets.QLineEdit.Password)


    def upload_sample_info(self):    #function to upload barcode-sampleID file
        try:
            #select file from directory -> only allowing .csv/.tsv/.xlsx-files
            self.SAMPLE_INFO_FILE_PATH, _ = QFileDialog.getOpenFileName(self, 'Select sample sheet',"~", "data files(*.csv *.tsv *.xlsx)")
            
            
            
            #get file-name and suffix
            FILENAME =  QFileInfo(self.SAMPLE_INFO_FILE_PATH).fileName()
            self.SAMPLE_INFO_FILE_SUFFIX = FILENAME.split(".",1)[1]

            #pass variables to WINDOW2 variables (WINDOW2_libraries.py) for use there
            self.WINDOW2.SAMPLE_INFO_FILE_PATH = self.SAMPLE_INFO_FILE_PATH
            self.WINDOW2.SAMPLE_INFO_FILE_SUFFIX = self.SAMPLE_INFO_FILE_SUFFIX

            #execute WINDOW2
            self.WINDOW2.open_sheet()
            
        except IndexError:
            print('no file selected')


    def info(self): #function to show info-text for uploading a sample info-sheet (.csv/.tsv/.xlsx) in message-window
        MSG_SAMPLE_SHEET_INFO = QMessageBox()   #set up message-window
        MSG_SAMPLE_SHEET_INFO.setWindowTitle("data input")  #set title for message; text is set text below
        MSG_SAMPLE_SHEET_INFO.setText("If you wanna use 96 samples, please create a csv (comma-separated; .csv), tsv (tab-separated; .tsv) or excel (.xlsx) file as shown in the main window.\n\nIn case of a .csv file use comma and not semicolon!\nRemember to write the headers (\"barcode\", \"sample_id\") not in caps.")
        x = MSG_SAMPLE_SHEET_INFO.exec_()   #open message
