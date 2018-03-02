#!/usr/bin/python

import smtplib, copy, sys
import socket

#####################################
#		notify.py
#
#	Any and all notifcation related activities for Release Automation
#
#####################################
class email:
	def __init__(self):
		self.SmtpServer = "mail.sh.mvista.com"
		self.Sender = "bugz-auto@mvista.com"
		self.BugzEmail = 'bugz-mail@sh.mvista.com'
		self.ReleaseEmail = 'release-request@mvista.com'

		self.Header = ""

		return
	

	def send(self, to_list, subject, message):
		if socket.gethostname() == 'pinocchio':
			return

		email_list = copy.deepcopy(to_list)
		email_list.append(self.BugzEmail)
		email_list.append(self.ReleaseEmail)

		msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
			% (self.Sender, ", ".join(email_list), subject))

		msg += "release.sh.mvista.com\r\n\r\n"
		msg += message


		####
		##DEBUG
		#print msg
		#return
		####

		try:
			server = smtplib.SMTP(self.SmtpServer)
			server.sendmail(self.Sender, email_list, msg)
			server.quit()
		except:
			return False
		return True
#end email
def main():
	sys.stderr.write('No manual execution of this module\n');
	sys.exit(1)


if __name__=="__main__":
	main()


