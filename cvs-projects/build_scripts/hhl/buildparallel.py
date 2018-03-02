#!/usr/bin/python

import sys, os, string, shutil

builddir = sys.argv[1]
userpath = sys.argv[2]
target = sys.argv[3]
kernel = sys.argv[4]
lsppath = sys.argv[5]
lspbuildpath = sys.argv[6]
toolpath = sys.argv[7]
cpdir = sys.argv[8]
buildid = sys.argv[9]
hhlversion = sys.argv[10]
buildme = sys.argv[11]
logdir = sys.argv[12]
installdir = sys.argv[13]
rcfile = sys.argv[14]
lspdat = sys.argv[15]
lsprev = sys.argv[16]
lsppatch = sys.argv[17]
product = sys.argv[18]
rpmbin = sys.argv[19]

rpmdb = installdir + '/rpmdb'
dbpath = installdir + '/rpmdb2'


def main():
  os.chdir(builddir)

  os.system("rm -rf %s && cp -a %s/rpmdb %s" %(dbpath, installdir, dbpath))

  pid = os.fork()
  if pid == 0:
    log = "%s/apps-%s-%s.log" % (logdir, target, buildid)
    os.system('./buildtargetapps.py %s %s %s %s %s %s %s %s %s %s > %s 2>&1' %
        (userpath, toolpath, target, buildme, buildid, cpdir, rpmdb, rcfile, product, rpmbin, log))
 
  else:
    log = "%s/lsp-%s-%s.log" % (logdir, target, buildid)
    os.system('./buildlsp.py %s %s %s %s %s %s %s %s %s %s %s %s %s %s > %s 2>&1' %
        (builddir, lspbuildpath, target, kernel,
         lsppath, cpdir, buildid, hhlversion, dbpath, rcfile, lspdat, lsprev, lsppatch, rpmbin, log))

    #wait for targetapps...
    os.waitpid(pid, 0)

if __name__ == "__main__":
  main()
