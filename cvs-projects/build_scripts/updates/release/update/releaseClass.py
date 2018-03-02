#!/usr/bin/python

import sys

class ReleaseJob:
	def __init__(self, funcName, className, moduleName, class_args, method_args, jobId, cmd=None):
		self.funcName = funcName
		self.className = className
		self.moduleName = moduleName
		self.class_args = class_args
		self.method_args = method_args
		self.jobId = jobId
		self.cmd=None



