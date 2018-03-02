#!/usr/bin/python

import os,sys,string

os.chdir("/mvista/ftp/arch")
for dir in os.popen('ls -d *').readlines():
  dir = string.replace(dir, '\012','')
  if os.path.exists('/mvista/ftp/arch/%s/updates/gcc-3.4.3-25.0.136.0703282'%(dir)):
    print "cleaning %s"%(dir)
    os.system('rm -rf /mvista/ftp/arch/%s/updates/gcc-3.4.3-25.0.136.0703282'%(dir))
