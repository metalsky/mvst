#!/usr/bin/python
import sys, os, string, re, getopt, time

# Args:
# 1- conf file
# 2- buildtag
# 3- cddir
# 4- scripttest

def gettime():
  t_time = time.localtime(time.time())
  s_time = time.strftime("%H:%M:%S %Z %Y/%m/%d",t_time)
  f_time = time.mktime(t_time)
  return s_time + ' [' + str(f_time) + ']'

if len(sys.argv) == 1:
  print 'usage: %s %s %s %s %s' % (sys.argv[0],'<conf file>','<buildtag>','<cddir>','<scripttest>')
  sys.exit(1)

conf = sys.argv[1]
print 'conf = ' + conf
exec(open(conf))
buildtag = sys.argv[2]
cddir = sys.argv[3] 
scripttest = sys.argv[4]
logdir = cddir + '/../../logs/' + buildtag

print "Copying images & lsp logs to vision at %s ..." % (gettime())
sys.__stdout__.flush()
if apocalypsepath:
  # remove & create directories
  if scripttest in ('true','false'):
    print 'ssh ftpadmin@vision "rm -rf %s/*"' % (apocalypsepath)
  else:
    os.system('ssh ftpadmin@vision "rm -rf %s/*"' % (apocalypsepath))
  if scripttest in ('true','false'):
    print 'ssh ftpadmin@vision "mkdir -p %s/%s"' % (apocalypsepath,buildtag)
  else:
    os.system('ssh ftpadmin@vision "mkdir -p %s/%s"' % (apocalypsepath,buildtag))

  # copy images
  for image in apocimages:
    if scripttest in ('true','false'):
      print 'scp %s/*%s* ftpadmin@vision:%s/%s' % (cddir,image,apocalypsepath,buildtag)
    else:
      os.system('scp %s/*%s* ftpadmin@vision:%s/%s' % (cddir,image,apocalypsepath,buildtag))

  # copy md5sum log
  if scripttest in ('true','false'):
    print 'scp %s/README* ftpadmin@vision:%s/%s' % (cddir,apocalypsepath,buildtag)
  else:
    os.system('scp %s/README* ftpadmin@vision:%s/%s' % (cddir,apocalypsepath,buildtag))

  # copy lsp log files
  for image in apocimages:
    if image != 'host':
      if scripttest in ('true','false'):
        print 'scp %s/lsp-%s* ftpadmin@vision:%s/%s' % (logdir,image,apocalypsepath,buildtag)
      else:
        os.system('scp %s/lsp-%s* ftpadmin@vision:%s/%s' % (logdir,image,apocalypsepath,buildtag))

  print "Finished copying lsp logs and images to vision at %s ..." % (gettime())
  sys.__stdout__.flush()
else:
  print 'vision path is null, skipping copying cd images to vision'
  sys.__stdout__.flush()

