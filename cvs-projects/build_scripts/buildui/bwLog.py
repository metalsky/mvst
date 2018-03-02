#!/usr/bin/env python
import logging
from DEBUG import *
DEBUG = isDebugMode()

class bwLog:
	def __init__(self):
		self.log = logging.getLogger("BuildWeb")
		#if DEBUG:
		#	fh = logging.FileHandler("test.log")
		#else:
		fh = logging.FileHandler("/var/log/buildweb.log")
		fh.setLevel(logging.DEBUG)
		formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(message)s")
		fh.setFormatter(formatter)
		self.log.addHandler(fh)
		self.log.setLevel(logging.DEBUG)

	def info(self,msg):
		self.log.info(msg)
	
	def warn(self,msg):
		self.log.warn(msg)
	




