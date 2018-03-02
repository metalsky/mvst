#!/usr/bin/python


import smtplib, telnetlib


def sendPage(msgSender, msgRecipient, msgBody):
	server = smtplib.SMTP("mail.mvista.com")
	server.sendmail(msgSender, msgRecipient, msgBody)
	server.quit()


def checkPort(host, port):
	try:
		x = telnetlib.Telnet(host, port)
		print x.read_some()
		x.close()
	except:
		msgText = "Critical! Overlord's SSHD isn't responding!!"
		sendPage(msgSender, msgRecipient, msgText)


port = "22"
host = "10.23.5.3"
msgSender = "build@mvista.com"
msgRecipient = "6508042674@txt.att.net"


checkPort(host, port)
