#!/usr/bin/python
import os, string, sys, shutil, time

def gettime():
  t_time = time.localtime(time.time())
  s_time = time.strftime("%H:%M:%S %Z %Y/%m/%d",t_time)
  f_time = time.mktime(t_time)
  return s_time + ' [' + str(f_time) + ']'

def mstart(app):
  print '<' + sys.argv[0] + '>: building ' + app + ' at ' + gettime() + '...'
  sys.__stdout__.flush()

def mstop(app):
  print '<' + sys.argv[0] + '>: finished ' + app + ' at ' + gettime() + '...'
  sys.__stdout__.flush()


