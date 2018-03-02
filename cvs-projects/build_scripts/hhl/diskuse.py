#!/usr/bin/python
import os, string, sys

def getusage(logfile,retval=1):
  f_logfile = open(logfile,'r')
  loglist = f_logfile.readlines()
  f_logfile.close()
  diskUseList = []
  linenum = 0
  length = len(loglist)
  minUsage = 0
  maxUsage = 0
  while linenum < length:
    if string.find(loglist[linenum],'1k-blocks') != -1:
      diskUseList.append(string.split(string.strip(loglist[linenum+1]))[2])
    linenum+=1
  if diskUseList:
    minUsage = string.atoi(diskUseList[0])
    maxUsage = string.atoi(diskUseList[0])
  for usage in diskUseList:
    if string.atoi(usage) > minUsage:
      # a large number means more disk is available
      minUsage = string.atoi(usage)
    if string.atoi(usage) < maxUsage:
      # a small number means less disk is available
      maxUsage = string.atoi(usage)
  totalUsage = minUsage - maxUsage
  if retval:
    return totalUsage
  else:
    print totalUsage

if __name__ == '__main__':
  if len(sys.argv) == 2:
    getusage(sys.argv[1],0)
  else:
    print "Usage: diskusage.py <logfile>"

