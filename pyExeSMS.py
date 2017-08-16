#!/usr/bin/python

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import requests
import configparser
from os.path import isfile

def readConfig():
	global username
	global password
	global debugLogging
	global myMobileNumber

	configfile = 'pyExeSMS.ini'

	if not isfile(configfile):
		print('Failed to read configuration file. Is ' + configfile + ' present?')
		confirmExit()

	logger("Reading " + configfile)
	config = configparser.ConfigParser()
	config.read(configfile)

	logger("Parsing " + configfile)
	try:
		username = config['pyExeSMS']['username']
		logger("Username: " + username)
		password = config['pyExeSMS']['password']
		logger("Password: " + password)
		debugLogging = config['pyExeSMS'].getboolean('debuglogging')
		logger("debugLogging: " + str(debugLogging))
		myMobileNumber = config['pyExeSMS']['mymobilenumber']
		logger("myMobileNumber: " + myMobileNumber)
	except Exception as e:
		print('Failed to parse configuration file. Is it formatted correctly?')
		logger(e)
		confirmExit()

def confirmExit():
	input('\nPress the Enter key to exit')
	exit(0)

def logger(msg):
	if debugLogging:
		x = str(msg)
		msglines = x.splitlines()
		for x in msglines:
			print("Debug: " + x)
	return msg

def sendMessage(*args):
	global count
	logger(username + password + myMobileNumber)
	logger("Trying to send.")
	to = destnum.get()
	to = "".join(to.split())
	if to.isdecimal() and len(to) == 10:
		logger("to is decimal and 10 chars long.")
		logger("To: " + to)
	else:
		logger("to isn't decimal or isn't 10 chars long.")
		logger("To: " + to)
		messagebox.showwarning("Bad Destination", "Destination mobile number should be 10 numerical digits long.\nE.g. 0412345678 or 0412 345 678\nMessage not sent.")
		return
	message = message_text.get("1.0", END)
	message = message.strip()
	message = " ".join(message.splitlines())
	logger("Message: \"" + message + "\"")
	if len(message) == 0:
		logger("Message empty.")
		messagebox.showwarning("Empty Message", "The message seems to be empty.")
		return
	if len(message) > 600:
		logger("Message too long.")
		messagebox.showwarning("Message Too Long", "The message is too long.\nIt was " + str(len(message)) + " characters. 600 is the limit.")
		return
	try:
		# Send the message
		logger("Sending...")
		count += 1
		pokeURL(to, message)
	except requests.exceptions.RequestException as e:
		print(str(e))
		logger(e)
		messagebox.showwarning("Error", str(e))
		return
	return

def pokeURL(to, msg):
	logger("Sending...")
	baseurl = "https://smsgw.exetel.com.au/sendsms/api_sms.php"
	payload = {'username': username, 'password': password, 'mobilenumber': to, 'message': msg, 'sender': sourcenum.get(), 'messagetype': 'Text', 'referencenumber': count}
	r = requests.get(baseurl, params=payload)
	logger("URL: " + str(r.url))
	logger("HTTP status code " + str(r.status_code))
	logger(r.text)
	if r.status_code != requests.codes.ok:
		messagebox.showwarning("Server reported status code: " + str(r.status_code))
	logger(str(r.text.split('|')))
	status = r.text.split('|')[4]
	messagebox.showinfo("Message Sent", "Server replied: " + status)
	return

root = Tk()
root.title("pyExeSMS")

username = ""
password = ""
myMobileNumber = ""
# This debugLogging value will be overwritten by the one in the config file when it's read, so
# this value really only affects debugging while reading the config file.
debugLogging = False
readConfig()

sourcenum = StringVar()
destnum = StringVar()
count = 0

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

ttk.Label(mainframe, text="Send SMS", font=("Helvetica", 20)).grid(column=0, row=0, sticky=N, columnspan=5)
ttk.Label(mainframe, text="To:").grid(column=0, row=1, sticky=W)
ttk.Label(mainframe, text="From:").grid(column=3, row=1, sticky=E)
ttk.Label(mainframe, text="Message:").grid(column=0, row=2, sticky=W)

sourcenum_entry = ttk.Entry(mainframe, width=12, textvariable=sourcenum, state="readonly")
sourcenum_entry.grid(column=4, row=1, sticky=(W))
sourcenum.set(myMobileNumber)

destnum_entry = ttk.Entry(mainframe, width=14, textvariable=destnum)
destnum_entry.grid(column=1, row=1, sticky=(W))

message_text = Text(mainframe, width=80, height=8, wrap=WORD)
message_text.grid(column=1, row=2, sticky=(W), columnspan=4)

ttk.Button(mainframe, text="Send", command=sendMessage).grid(column=4, row=3, sticky=E)

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

destnum_entry.focus()
#root.bind('<Return>', sendMessage)
root.mainloop()