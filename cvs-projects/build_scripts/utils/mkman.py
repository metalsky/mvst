#!/usr/bin/python
import os, string, sys

print '<update-site>'

print ' <packages type="mvl-rpm">'
for a in os.popen('find . -regex ".+.mvl\|.+.rpm" -print').readlines():
     print '  <package>'
     rpmval = os.popen('rpm -qp ' + string.strip(a) + ' --qf "%{NAME}:%{VERSION}:%{RELEASE}:%{ARCH}:%{SIGMD5}:%{SHA1HEADER}"').read()
     rpmvals = string.split(rpmval,':')
     filepath = os.popen('find ' + string.strip(a) + ' -printf \%p').read()
     size = os.popen('find ' + string.strip(a) + ' -printf \%s').read()
     try:
       print '   <name>%s</name>' % rpmvals[0]
       print '   <version>%s</version>' % rpmvals[1]
       print '   <release>%s</release>' % rpmvals[2]
       print '   <target>%s</target>' % rpmvals[3]
       print '   <sigmd5>%s</sigmd5>' % rpmvals[4]
       print '   <signature>%s</signature>' % rpmvals[5]
       print '   <filepath>%s</filepath>' % string.strip(filepath)
       print '   <size>%s</size>' % string.strip(size)
       print '  </package>'
     except:
       sys.stderr.write("Error: Bad rpm %s"%(a))
print ' </packages>'

print ' <patches type="kernel">'
for a in os.popen('find . -regex ".+.patch" -print').readlines():
     print '  <patch>'
     filepath = os.popen('find ' + string.strip(a) + ' -printf \%p').read()
     size = os.popen('find ' + string.strip(a) + ' -printf \%s').read()
     print '   <filepath>%s</filepath>' % string.strip(filepath)
     print '   <size>%s</size>' % string.strip(size)
     print '  </patch>'
print ' </patches>'

print '</update-site>'

