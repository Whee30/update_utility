import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit
from PyQt6.QtCore import Qt, QTimer
import os
#import pyi_splash
import hashlib
import json
import time
import requests

required_items = {
    "output":"./output",
    "sources":"./sources",
    "previousWarrants":"./sources/previousWarrants",
    "TandE":"./sources/TandE.txt",
    "program":"./warrantBuilder.exe",
    "verbiage":"./sources/cv_sources.json",
    "template":"./sources/skeleton.docx",
    "settings":"./sources/settings.json",
}

no_cache_headers = {
    'Cache-Control': 'no-cache'
}

# Your remotely hosted hash list that will be used to compare against the remote files.
# Ideally, I would imagine this is best hosted independently from the files to further increase security.
remote_hash_list = "<URL to remote hash list>"

# Declare the global dictionary for the hashes
hash_references = {}

# The files needing hash validation and set to be downloaded
# Private hosting, github, Google drive etc...
remote_files = {
    "program":"<remotely hosted file>",
    "verbiage":"<remotely hosted file>",
    "template":"<remotely hosted file>",
    "settings":"<remotely hosted file>"
}

# The expected locations of the local files to be checked
local_files = {
    "program":"./warrantBuilder.exe",
    "verbiage":"./sources/cv_sources.json",
    "template":"./sources/skeleton.docx",
    "settings":"./sources/settings.json"
}

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Warrant Builder - Update Utility v0.1")
        self.setFixedWidth(300)

        #####################
        # ESTABLISH WIDGETS #
        #####################

        self.main_label = QLabel("Warrant Builder Update Utility")

        self.status_report = QTextEdit()

        self.submit_button = QPushButton()
        self.submit_button.setText("Upgrade!")
        self.submit_button.setFixedWidth(100)
        self.submit_button.clicked.connect(lambda: self.run_update())
        self.submit_button.setEnabled(False)

        self.quit_button = QPushButton()
        self.quit_button.setText("Quit")
        self.quit_button.setFixedWidth(100)
        self.quit_button.clicked.connect(QApplication.instance().quit)
        self.quit_button.setEnabled(False)

        ########################
        # Establish the layout #
        ########################

        self.main = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.main.setLayout(self.main_layout)

        self.button_row = QWidget()
        self.button_row_layout = QHBoxLayout()
        self.button_row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.button_row.setLayout(self.button_row_layout)
        self.button_row_layout.setSpacing(20)

        #######################
        # Add widgets to main #
        #######################

        self.main_layout.addWidget(self.main_label)

        self.main_layout.addWidget(self.status_report)

        self.main_layout.addWidget(self.button_row)

        self.button_row_layout.addWidget(self.submit_button)
        self.button_row_layout.addWidget(self.quit_button)

        self.setCentralWidget(self.main)

        #######################
        # Establish Functions #
        #######################

    # Function to compare hashes of remote files against local files.
    def compare_hashes(self, k):
        hash_to_compare = hash_references[k]
        remote_sha256_hash = hashlib.sha256()
        # If there are internet connection issues, this should throw an error.
        try:
            response = requests.get(remote_files[k], headers=no_cache_headers)
        except:
            self.status_report.append("Connection to remote files could not be made. Please check your internet connection and try again.")
            QApplication.processEvents() 
            return False
        remote_sha256_hash.update(response.content)
        # If the calculated and listed hashes match, the file will be downloaded
        if remote_sha256_hash.hexdigest() == hash_to_compare:
            self.replace_file(k)
            print(f"The {k} file was updated.")
            QApplication.processEvents() 
        # If not, the files and hashes should be examined for what's rotten in Denmark
        elif remote_sha256_hash.hexdigest() != hash_to_compare:
            print(f"The hashes don't match! Something's wonky in dolphin-town. The {k} file was not replaced.")
            print(f"{k} calculated: {remote_sha256_hash.hexdigest()}")
            print(f"{k} Stored:     {hash_to_compare}")
            self.status_report.append(f"Something went wrong with the {k} file, it was not updated.")
            QApplication.processEvents() 

    # This function completes the download of files into their expected positions.
    def replace_file(self, k):
        file_response = requests.get(remote_files[k], headers=no_cache_headers)
        with open(local_files[k], 'wb') as file:
            file.write(file_response.content)

    # The function called from the Submit button.
    def run_update(self):
        self.status_report.append("Comparing file versions...")
        QApplication.processEvents() 
        for k, v in local_files.items():
            hash_to_compare = hash_references[k]
            local_file_hash = hashlib.sha256()
            with open(v, "rb") as file:
                local_file_hash.update(file.read())
            if local_file_hash.hexdigest() != hash_to_compare:
                self.compare_hashes(k)
        self.status_report.append("All files are up to date!")
        QApplication.processEvents() 

    # The function that runs after the window loads. Checks for existing/missing files. If files are missing, the hashes will be checked
    # and the missing files will be downloaded. Because of this, you can start with *just* the updater and get the whole program.
    def initial_processing(self):
        global hash_references
        try:
            h_response = requests.get(remote_hash_list, headers=no_cache_headers)
            hash_references = h_response.json()
        except:
            self.status_report.append("Connection to remote files could not be made. Please check your internet connection and try again.")
            QApplication.processEvents() 
            return False
        self.status_report.append("Checking for all required files...")
        QApplication.processEvents() 
        # Check for required directories and files        
        if os.path.exists('./output') == False:
            os.mkdir('./output')
            self.status_report.append("Output directory missing, directory was created.")
            QApplication.processEvents() 
        if os.path.exists('./sources') == False:
            os.mkdir("./sources")
            self.status_report.append("sources directory missing, directory was created.")
            QApplication.processEvents() 
        if os.path.exists('./sources/previousWarrants') == False:
            os.mkdir('./sources/previousWarrants')
            self.status_report.append("Previous warrants directory missing, directory was created.")
            QApplication.processEvents()       
        if os.path.exists('./sources/TandE.txt') == False:
            with open("./sources/TandE.txt", "w") as file:
                file.write("This is where you include your relevant experience")
            self.status_report.append("Training file was missing, file was created.")
            QApplication.processEvents() 
        for k, v in required_items.items():
            if os.path.exists(v) == False:
                self.status_report.append(f"{k} file was missing, downloading file...")
                QApplication.processEvents() 
                self.compare_hashes(k)
                self.status_report.append(f"{k} file was downloaded.")
                QApplication.processEvents() 
        self.status_report.append("All files are present.")
        # Once the initial processing is complete, files are downloaded if needed etc., the buttons are enabled.
        self.quit_button.setEnabled(True)
        self.submit_button.setEnabled(True)
        
app = QApplication(sys.argv)

#pyi_splash.close()
window = MainWindow()
window.show()
app.setStyle('Fusion')

QTimer.singleShot(100, window.initial_processing)

app.exec()
