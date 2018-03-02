#!/usr/bin/python
import getopt
from buildFunctions import *
from resourceManager import *
from builddefs import *
from verifyNode import *

# installimage.py

# This script installs the host installer, creates the host cdimage
# It then installs the target installer and creates the target cdimage(s)
# if you only want one type, i.e host|target you set this in <product>data.dat
# if you don't want to create all of your editions target cds you can set arch to which
# target you want the installer and cdimage(s) created for in <product>data.dat.

def makeIso(buildtag,buildid,cdtempdir,mkisocmd,cdtype,cddir,logdir,product):
  while 1:
    cdnode = getResource(buildtag,buildid,nodetype,"Making CD Images")
    cdnodeVerify = verifyNode(cdnode,'none')
    if cdnodeVerify == SUCCESS:
      break
    else:
      msg = 'verifyNode failed for %s in %s in makeIso' % (cdnode,buildtag)
      subject = 'verifyNode Failed for %s' % cdnode
      logmsg = '%s failed verification, it will remain checked out using %s buildtag' % (cdnode,buildtag)
      mailError(msg,subject,cdnode,buildtag,logmsg,reslog,scripttest)
  print "making %s cd on %s..." % (cdtype,cdnode)
  sys.__stdout__.flush()
  #print "mkisocmd:"
  #print mkisocmd
  #sys.__stdout__.flush()
  os.system('ssh %s "mkdir -p %s; cd %s; %s"' % (cdnode,cdtempdir,cdtempdir,mkisocmd))
  os.system('ssh %s "cd %s; md5sum *.iso > md5sum"' % (cdnode,cdtempdir))
  os.system('ssh %s "cp %s/*.iso %s"' % (cdnode,cdtempdir,cddir))
  r_md5sum = getResource(buildtag,buildid,"md5sum","Adding %s-%s-%s md5sum" %(cdtype,product,buildid))
  os.system('ssh %s "cat %s/md5sum >> %s/README.md5sum"' % (cdnode,cdtempdir,cddir))
  releaseResource(r_md5sum)
  os.system('ssh %s "touch %s/%s-image-done; cd /; rm -rf %s"' % (cdnode,logdir,cdtype,cdtempdir))
  releaseResource(cdnode)
  return

def targetIsoThrd(buildtag,buildid,cdtempdir,mkisocmd,cdtype,cddir,logdir,target):
  while 1:
    cdnode = getResource(buildtag,buildid,nodetype,"Making CD Images")
    cdnodeVerify = verifyNode(cdnode,'none')
    if cdnodeVerify == SUCCESS:
      break
    else:
      msg = 'verifyNode failed for %s in %s in targetIsoThrd' % (cdnode,buildtag)
      subject = 'verifyNode Failed for %s' % cdnode
      logmsg = '%s failed verification, it will remain checked out using %s buildtag' % (cdnode,buildtag)
      mailError(msg,subject,cdnode,buildtag,logmsg,reslog,scripttest)
  print "making %s iso for %s on %s..." % (cdtype,target,cdnode)
  sys.__stdout__.flush()
  #print "mkisocmd:"
  #print mkisocmd
  #sys.__stdout__.flush()
  os.system('ssh %s "mkdir -p %s; cd %s; %s"' % (cdnode,cdtempdir,cdtempdir,mkisocmd))
  os.system('ssh %s "cd %s; md5sum %s-*.iso > md5sum"' % (cdnode,cdtempdir,cdtype))
  if not os.path.exists(cddir):
    os.system('mkdir -p %s' % cddir)
  os.system('ssh %s "cp %s/%s-*.iso %s"' % (cdnode,cdtempdir,cdtype,cddir))
  r_md5sum = getResource(buildtag,buildid,"md5sum","Adding md5sum to README.md5sum")
  md5sum = os.popen('ssh %s "cat %s/md5sum"' % (cdnode,cdtempdir)).read()
  print md5sum
  f_md5sum = open('%s/README.md5sum' % cddir,'a')
  f_md5sum.write(md5sum)
  f_md5sum.close()
  releaseResource(r_md5sum)
  os.system('ssh %s "touch %s/%s-%s-image-done; cd /; rm -rf %s"' % (cdnode,logdir,cdtype,target,cdtempdir))
  releaseResource(cdnode)
  return


if len(sys.argv) == 1:
  print 'usage: %s %s' % (sys.argv[0],'<data file>')
  sys.exit(1)

conf	= sys.argv[1]

header = [ "The following information is the MD5 checksums of each file",
          "contained in this directory.  This information is used to",
          "verify that the files downloaded from this directory were not",
          "corrupted during the transfer.",
          " ",
          "            md5sum                          file",
          "--------------------------------  ---------------------------"]

body = [ "This README is a place holder for the product documentation",
          "--------------------------------  ---------------------------"]

# set all variables for installing installers and making cds to 0 by default so that data.dat files only
# need to specify what cd/installs they want rather than all possible...will simplify adding new cd/installs
commoncdinstall = 0
#------------------------------------------------------------------------------------------
# Read <product>data.dat 
#------------------------------------------------------------------------------------------
builddir = os.getcwd()
exec(open(conf))
if product in ('dev','fe'):
	product = 'foundation'
elif product == 'mtb':
        product = 'mobilinux'
print 'product = ' + product
print 'cpdir = ' + cpdir
print 'buildid = ' + buildid
print 'buildtag = ' + buildtag
kernelinfo = kernel + '_' + hhlversion
print 'kernelinfo = ' + kernelinfo

#volume file stuff:
old = ('-00000')
new = ('-00001')

cddir = copydir + '/' + buildtag + '/cdimages'
print 'cddir = ' + cddir
dvddir = copydir + '/' + buildtag + '/dvdimages'
print 'dvddir = ' + dvddir
os.system('mkdir -p ' + cddir)
os.system('mkdir -p ' + dvddir)
# make a temporary cd directory to build cdimages locally
cdtempdir = '/var/tmp/CDTEMP'
os.system('mkdir -p ' + cdtempdir)
installrpmdir = cpdir + '/installer_rpms'
iadir = installrpmdir + '/install_area'
voldir = '/etc/config/volume'
shidir = installrpmdir + '/install_area//self-hosted'
print 'self_hosted_installdir = ' + shidir
cidir = installrpmdir + '/install_area//cross'
print 'cross_installdir = ' + cidir
cmnidir = installrpmdir + '/install_area//common'
print 'common_installdir = ' + cmnidir
tidir = installrpmdir + '/install_area//target'
print 'target_installdir = ' + tidir
lidir = installrpmdir + '/install_area//lsps'
print 'lsps_installdir = ' + lidir
hidir = installrpmdir + '/install_area//host'
print 'host_installdir = ' + hidir
didir = installrpmdir + '/install_area//docs-cd'
print 'docs_installdir = ' + didir
dvdidir = installrpmdir + '/install_area//dvd'
print 'dvd_installdir = ' + dvdidir

mkisofscmd = 'mkisofs -quiet -r -J -joliet-long -allow-leading-dots -no-split-symlink-components -no-split-symlink-fields '

if os.path.exists('/tmp/rpmdb'):
  os.system('rm -rf /tmp/rpmdb')
if os.path.exists('/tmp/rpmdbsudo'):
  os.system('rm -rf /tmp/rpmdbsudo')
os.system('cp -a /var/lib/rpm /tmp/rpmdb')
os.system('cp -a /var/lib/rpm /tmp/rpmdbsudo')

for headerdir in (cddir,dvddir):
  os.chdir(headerdir)
  r_md5sum = getResource(buildtag,buildid,"md5sum","Adding md5sum to README.md5sum")
  for h in header:
    os.system('echo "' + h + '" >> README.md5sum')
  releaseResource(r_md5sum)
os.chdir(builddir)
logdir = copydir + '/' + buildtag + '/logs'

cdhosts = []
for host in chroothosts:
  cdhosts.append(host)
for host in hosts:
  cdhosts.append(host)
#------------------------------------------------------------------------------------------
if hostcdinstall:
  print '<' + sys.argv[0] + '>: checking for the host installer for ' + sys.argv[1] + ' ' + buildid + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
  sys.__stdout__.flush()
#-----------------------------------------------------------------------------------------
# Let's check for the host-mvl-installer-build-3.1-<build-id>.noarch.mvl
#------------------------------------------------------------------------------------------
  for h in cdhosts: 
    hf = string.strip(os.popen('ls ' + installrpmdir + '/host/' + h + '/*cd-installer*').read())
    if not os.path.exists(hf):
      print 'host-cd-installer.mvl does not exist for host ' + h + ' ... skipping '
    #if it's there let's install it
    else:
      print 'installing host-cd-installer.mvl for host ' + h + ' ...'
      sys.__stdout__.flush()
      rpmdb = getResource(buildtag,buildid,"dumborpmdb","Installing installer rpms")
      os.system('rpm --dbpath /tmp/rpmdb -ihv  ' + installrpmdir + '/host/' + h + 
                '/host-cd-installer*.mvl --prefix ' + hidir + 
                ' --nodeps --force --ignoreos --ignorearch')
      releaseResource(rpmdb)
      sys.__stdout__.flush()

  # Change the volume file for the hostcd
  os.chdir(iadir + '/host' + voldir)
  contents = os.listdir('.')
  for c in contents:
    print 'For ' + c + ' moving ' + old + ' to ' + new + ' ...'
    os.system('mv ' + c + ' ' + string.replace(c,old,new))
    sys.__stdout__.flush()
  # Copy the installed components to cpdir for NFS installs
  os.system('cp -a ' + hidir + '/* ' + cpdir)
#------------------------------------------------------------------------------------------
# Now let's create the host cdimage
#------------------------------------------------------------------------------------------
  print 'creating the host cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
  sys.__stdout__.flush()
if mkhostcd:
  #make host images
  cd = 'host'
  mkisocmd = mkisofscmd + '-V ' + cd + ' -o ' + cd + '-' + product + '-' + buildid + '.iso '
  mkisocmd = mkisocmd + '-x cluster -x done -x SRPMS -x testing '
  xclude = []
  xcludedirs = []
  os.chdir(cpdir + '/host/common')
  contents = os.listdir('.')
  for c in contents:
    for o in outtakes:
      if string.find(string.strip(c),o + '-') != -1:
        xclude.append(string.strip(c))
  os.chdir(cpdir + '/host')
  for h in cdhosts:
    if os.path.exists(cpdir + '/host/' + h):
      os.chdir(cpdir + '/host/' + h)
      contents = os.listdir('.')
      for c in contents:
        for o in outtakes:
          if string.find(string.strip(c),o + '-') != -1:
            xclude.append(string.strip(c))
  os.chdir(cpdir + '/host/common/optional')
  contents = os.listdir('.')
  for c in contents:
    if string.find(string.strip(c),'host-kernel-' + kernelinfo) == -1:
      xclude.append(string.strip(c))
  os.chdir(cpdir + '/host')
  for x in xclude:
    #print 'excluding: ' + x + '...'
    mkisocmd = mkisocmd + '-x ' + x + ' '
  mkisocmd = mkisocmd + '-graft-points '
  if 'windows2000' in hosts:
    if os.path.exists(cpdir + '/autorun.inf'):
      mkisocmd = mkisocmd + 'autorun.inf=' + cpdir + '/autorun.inf '
    if os.path.exists(cpdir + '/mvista.ico'):
      mkisocmd = mkisocmd + 'mvista.ico=' + cpdir + '/mvista.ico '
  mkisocmd = mkisocmd + 'host/=' + cpdir + '/host/ '
  if os.path.exists(cpdir + '/host-tools'):
    mkisocmd = mkisocmd + 'host-tools/=' + cpdir + '/host-tools/ '
  for installdir in os.listdir(hidir):
    if os.path.isdir(hidir + '/' + installdir):
      mkisocmd = mkisocmd + installdir + '/=' + hidir + '/' + installdir + '/ '
  mkisocmd = mkisocmd + 'install=' + hidir + '/install '
  makeIso(buildtag,buildid,cdtempdir,mkisocmd,'host',cddir,logdir,product)
  if os.path.exists(logdir + '/host-image-done'):
    print "BUILT: host cdimage built"
  else:
    print "BUILD ERROR: host cdimage did not build."
  os.chdir(builddir)
#------------------------------------------------------------------------------------------
  print 'Finished creating the host cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
sys.__stdout__.flush()

# -----------------------------------------------------------------------------------------
# make common cd for devrocket
# -----------------------------------------------------------------------------------------
#
#if commoncdinstall:
#  print '<' + sys.argv[0] + '>: checking for the common installer for ' + sys.argv[1] + ' ' + buildid + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
#  sys.__stdout__.flush()
#  hf = string.strip(os.popen('ls ' + installrpmdir + '/common/devrocket-cd-installer*').read())
#  if not os.path.exists(hf):
#    print 'devrocket-cd-installer.mvl does not exist ... skipping ' + sys.argv[0] + ' ...'
#    sys.__stdout__.flush()
#  #if it's there let's install it
#  else:
#    print 'installing devrocket-cd-installer.mvl ...'
#    sys.__stdout__.flush()
#    rpmdb = getResource(buildtag,buildid,"dumborpmdb","Installing installer rpms")
#    os.system('rpm --dbpath /tmp/rpmdb -ihv  ' + installrpmdir + 
#              '/common/devrocket-cd-installer*.mvl --prefix ' +
#              cmnidir + ' --nodeps --force --ignoreos --ignorearch')
#    releaseResource(rpmdb)
#    sys.__stdout__.flush()
#    # Change the volume file for the hostcd
#    os.chdir(iadir + '/common' + voldir)
#    contents = os.listdir('.')
#    for c in contents:
#      print 'For ' + c + ' moving ' + old + ' to ' + new + ' ...'
#      os.system('mv ' + c + ' ' + string.replace(c,old,new))
#      sys.__stdout__.flush()
#    # Copy the installed components to cpdir for NFS installs
#    os.system('cp -a ' + cmnidir + '/* ' + cpdir)
if mkcommoncd:
  print '<' + sys.argv[0] + '>: building devrocket cd for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
  sys.__stdout__.flush()
  mkisocmd = mkisofscmd + '-V devrocket -o devrocket-' + buildid + '.iso '
  mkisocmd = mkisocmd + '-x cluster -x done -x i386 -x testing '
  mkisocmd = mkisocmd + '-graft-points '
  mkisocmd = mkisocmd + '/=' + cpdir + '/cd/ '
  for file in os.listdir('%s/results/archives' % cpdir):
    if string.find(file,'installer') > -1:
      mkisocmd = mkisocmd + file + '=' + cpdir + '/results/archives/' + file + ' '
  print 'makeIso command = ' + mkisocmd 
  sys.__stdout__.flush()
  makeIso(buildtag,buildid,cdtempdir,mkisocmd,'devrocket',cddir,logdir,product)
  if os.path.exists(logdir + '/devrocket-image-done'):
    print "BUILT: devrocket cdimage built"
  else:
    print "BUILD ERROR: devrocket cdimage did not build."
  os.chdir(builddir)
  print 'Finished creating the devrocket cdimage for ' + product + ' ' + buildid + ' at ' + gettime()
  sys.__stdout__.flush()
# -----------------------------------------------------------------------------------------
# make license-server cd for devrocket
# -----------------------------------------------------------------------------------------
#
if mklicensecd:
  printflush('<' + sys.argv[0] + '>: building license-server cd for ' + product + ' ' + buildid + ' at ' + gettime() + '...',scripttest)
  printflush('copying cd/* to dev_area...',scripttest)
  systemCmd('cp -a %s/cd/* %s' % (cvspaths['licensing'][0],cpdir))
  mkisocmd = mkisofscmd + '-V licserv -o license-server-' + buildid + '.iso '
  mkisocmd = mkisocmd + '-x build.done -x README.build '
  mkisocmd = mkisocmd + cpdir + '/ '
  makeIso(buildtag,buildid,cdtempdir,mkisocmd,'license-server',cddir,logdir,product)
  if os.path.exists(logdir + '/license-server-image-done'):
    printflush("BUILT: license-server cdimage built",scripttest)
  else:
    printflush("BUILD ERROR: license-server cdimage did not build.",scripttest)
  os.chdir(builddir)
  printflush('Finished creating the license-server cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + '...',scripttest)

#------------------------------------------------------------------------------------------
if targetcdinstall:
  print '<' + sys.argv[0] + '>: checking for arch-cd and self-hosted installers for ' + sys.argv[1] + ' ' + buildid +   ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
  sys.__stdout__.flush()
#-----------------------------------------------------------------------------------------
# Let's check for the arch-cd-installer.mvl
#------------------------------------------------------------------------------------------
  # install all cross-cd-installer rpms from installer_rpm/cross/<target>
  for target in os.listdir(installrpmdir + '/cross'):
    os.chdir(installrpmdir + '/cross/' + target)
    tf = string.strip(os.popen('ls *cd-install*').read())
    os.chdir(builddir)
    if not os.path.isfile(installrpmdir + '/cross/' + target + '/' + tf):
      print tf + ' does not exist for build ' + product + ' ' + buildid + ' ... skipping cross-cd-installer...'
    #if it's there let's install it
    else:
      rpmdb = getResource(buildtag,buildid,"dumborpmdb","Installing installer rpms")
      os.system('rpm --dbpath /tmp/rpmdb -ihv  ' + installrpmdir + '/cross/' + target + 
                '/' + tf + ' --prefix ' + cidir + '//' + target + ' --ignorearch --nodeps --force')
      releaseResource(rpmdb)

  # Change the volume file for the cross cd
    if os.path.exists(iadir + '/cross/' + target + voldir):
      os.chdir(iadir + '/cross/' + target + voldir)
      contents = os.listdir('.')
      for c in contents:
        print 'For ' + c + ' moving ' + old + ' to ' + new + ' ...'
        os.system('mv ' + c + ' ' + string.replace(c,old,new))
        sys.__stdout__.flush()
  # copy cross installers for NFS installs
  for target in os.listdir(cidir):
    os.system('cp -a ' + cidir + '/' + target + '/* ' + cpdir)

  # install all arch-cd-installer rpms from installer_rpm/target/<target>
  for target in os.listdir(installrpmdir + '/target'):
    os.chdir(installrpmdir + '/target/' + target)
    tf = string.strip(os.popen('ls *cd-install*').read())
    os.chdir(builddir)
    if not os.path.isfile(installrpmdir + '/target/' + target + '/' + tf):
      print tf + ' does not exist for build ' + product + ' ' + buildid + ' ... skipping arch-cd-installer...'
    #if it's there let's install it
    else:
      rpmdb = getResource(buildtag,buildid,"dumborpmdb","Installing installer rpms")
      os.system('sudo rpm --dbpath /tmp/rpmdbsudo -ihv  ' + installrpmdir + '/target/' + target + '/' + tf + ' --prefix ' + tidir + '//' + target + ' --ignorearch --nodeps --force')
      releaseResource(rpmdb)

  # Change the volume file for target cd
    if os.path.exists(iadir + '/target/' + target + voldir):
      os.chdir(iadir + '/target/' + target + voldir)
      contents = os.listdir('.')
      for c in contents:
        print 'For ' + c + ' moving ' + old + ' to ' + new + ' ...'
        os.system('sudo mv ' + c + ' ' + string.replace(c,old,new))
        sys.__stdout__.flush()
      # Move the required apps file ti etc/config/volume
      minReqFile = '%s/%s/MVL-%s-apps-%s-%s' % (cpdir,target,edition,target,buildid)
      if os.path.exists('%s' % minReqFile):
        os.system('sudo mv %s %s/target/%s%s' % (minReqFile,iadir,target,voldir))
  # copy target installers for NFS installs
  for target in os.listdir(tidir):
    os.system('sudo cp -a ' + tidir + '/' + target + '/* ' + cpdir)

  # install all lsp-cd-installer rpms from installer_rpm/lsps/<target>
  for target in os.listdir(installrpmdir + '/lsps'):
    os.chdir(installrpmdir + '/lsps/' + target)
    tf = string.strip(os.popen('ls *cd-install*').read())
    os.chdir(builddir)
    if not os.path.isfile(installrpmdir + '/lsps/' + target + '/' + tf):
      print tf + ' does not exist for build ' + product + ' ' + buildid + ' ... skipping lsp-cd-installer...'
    #if it's there let's install it
    else:
      rpmdb = getResource(buildtag,buildid,"dumborpmdb","Installing installer rpms")
      os.system('rpm --dbpath /tmp/rpmdb -ihv  ' + installrpmdir + '/lsps/' + target + 
                '/' + tf + ' --prefix ' + lidir + '//' + target + ' --ignorearch --nodeps --force')
      releaseResource(rpmdb)

  # Change the volume file for the lsp cd
    if os.path.exists(iadir + '/lsps/' + target + voldir):
      os.chdir(iadir + '/lsps/' + target + voldir)
      contents = os.listdir('.')
      for c in contents:
        print 'For ' + c + ' moving ' + old + ' to ' + new + ' ...'
        os.system('mv ' + c + ' ' + string.replace(c,old,new))
        sys.__stdout__.flush()
  # copy lsp installers for NFS installs
  for target in os.listdir(lidir):
    os.system('sudo cp -a ' + lidir + '/' + target + '/* ' + cpdir)

  # install self-hosted-installer rpms from installer_rpms/self-hosted/<target>
  if selfhosttarget != 'null':
    if os.path.exists(installrpmdir + '/self-hosted/' + selfhosttarget):
      os.chdir(installrpmdir + '/self-hosted/' + selfhosttarget)
      tf = string.strip(os.popen('ls *self-hosted-installer-* | grep -v debuginfo').read())
      os.chdir(builddir)
      if not os.path.isfile(installrpmdir + '/self-hosted/' + selfhosttarget + '/' + tf):
        print tf + ' does not exist for build ' + product + ' ' + buildid + ' ... skipping self-hosted-installer...'
        sys.__stdout__.flush()
      else:
        for installtarget in selfhostinstalldata.keys():
          rpmdb = getResource(buildtag,buildid,"dumborpmdb","Installing installer rpms")
          os.system('sudo rpm --dbpath /tmp/rpmdbsudo -ihv  ' + installrpmdir + '/self-hosted/' + selfhosttarget + '/' + tf + ' --prefix ' + shidir + '//' + installtarget + ' --ignorearch --nodeps --force')
          releaseResource(rpmdb)
        sys.__stdout__.flush()

      # install generic-mvl_install lsp or pc_target for cge:
      for installtarget in selfhostinstalldata.keys():
        x86lsp = selfhostinstalldata[installtarget][0] + '/lsps/' + selfhostinstalldata[installtarget][1]
        if os.path.exists(cpdir + '/' + x86lsp + '/target'):
          os.chdir(cpdir + '/' + x86lsp + '/target')
          tlspf = string.strip(os.popen('ls *.mvl').read())
          os.chdir(builddir)
          if not os.path.isfile(cpdir + '/' + x86lsp + '/target/' + tlspf):
            print tlspf + ' does not exist for build ' + product + ' ' + buildid + ' ... skipping isolinux configuration...'
            sys.__stdout__.flush()
          else:
            rpmdb = getResource(buildtag,buildid,"dumborpmdb","Installing installer rpms")
            os.system('sudo rpm --dbpath /tmp/rpmdbsudo -ihv  ' + cpdir + '/' + x86lsp + '/target/lsp*.mvl  --prefix '
                     + shidir + '//' + installtarget + ' --ignorearch --nodeps --force ')
            releaseResource(rpmdb)
            sys.__stdout__.flush()
            # Configure isolinux
            os.system('cd %s; sudo ./configure_isolinux.py %s %s %s %s %s/%s %s %s %s'
                       % (builddir,cpdir,selfhostinstalldata[installtarget][0],kernelinfo,edition,
                          shidir,installtarget,version,buildid,selfhostinstalldata[installtarget][1]))
            sys.__stdout__.flush()
            print 'configure_isolinux.py finished at ' + gettime()
            sys.__stdout__.flush()
            # now copy all self-hosted/target directories to all cross/<target> directories (x86 only) and
            # this may|may not change for new cd structure.  gay.
            print 'installtarget is ' + installtarget
            if string.find(installtarget,'x86') > -1:
              os.system('sudo cp -a ' + shidir + '/' + installtarget + '/* ' + tidir + '/' + installtarget)
    sys.__stdout__.flush()
  #------------------------------------------------------------------------------------------
  # Now let's create the target cdimages (cross, target, lsp)
  #------------------------------------------------------------------------------------------
if mktargetcd:
  for cdtype in cdnames:
    isoThrds = []
    print 'creating the ' + cdtype + ' cdimages for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
    sys.__stdout__.flush()
    #make target images
    cd_targets = all_targets
    if product in ('cgeasync','proasync','mobiasync',):
      cd_targets = lspIsos.keys()
    print 'cd_targets:'
    print cd_targets
    for cd in cd_targets:
      if cd in abitargets:
        continue
      ### This part forks off and does mkiso on other nodes, need to make this brm aware
      mkisocmd = mkisofscmd + '-V ' + cdtype + '-' + cd + ' -o ' + cdtype + '-' + cd + '-' + buildid + '.iso '
      mkisocmd = mkisocmd + '-x cluster -x testing '
      mkisocmd = mkisocmd + '-graft-points '
      xclude = []
      xcludedirs = []
      if cdtype == 'cross':
        xcludedirs = ['common',]
        for host in hosts:
          xcludedirs.append(host)
        for chroothost in chroothosts:
          xcludedirs.append(chroothost)
      elif cdtype == 'target':
        xcludedirs = ['optional',]
      elif cdtype == 'lsps':
        if cd in lspouttakes.keys():
          for dir in lspouttakes[cd]:
            xclude.append(dir)
      if os.path.exists(cpdir + '/' + cd + '/' + cdtype):
        os.chdir(cpdir + '/' + cd + '/' + cdtype)
        contents = os.listdir('.')
        for c in contents:
          for o in outtakes:
            if re.match(o,string.strip(c)): #if the outtake is matched at the beginning of the string
              xclude.append(string.strip(c))
        if re.search(r"uclibc", cd):
          for c in contents:
            for o in uclibc_outtakes:
              if re.match(o,string.strip(c)): #if the outtake is matched at the beginning of the string
                xclude.append(string.strip(c))
        for xd in xcludedirs:
          if os.path.exists(cpdir + '/' + cd + '/' + cdtype + '/' + xd):
            os.chdir(cpdir + '/' + cd + '/' + cdtype + '/' + xd)
            contents = os.listdir('.')
            for c in contents:
              for o in outtakes:
                if string.find(string.strip(c),o + '-') != -1:
                  xclude.append(string.strip(c))
      for x in xclude:
        mkisocmd = mkisocmd + '-x ' + x + ' '
      if cdtype == 'cross':
        for installdir in os.listdir(cidir + '/' + cd):
          mkisocmd = mkisocmd + installdir + '/=' + cidir + '/' + cd + '/' + installdir + '/ '
      elif cdtype == 'target':
        print 'install target is :' + cd
        if string.find(cd,'x86') > -1:
          if os.path.exists(shidir + '/' + cd + '/boot/isolinux/isolinux.bin'):
	    # Here are the options to enable isolinux native CD-ROM boot
	    # -l means allow long (up to 31 chars) iso9660 names for
	    #    the kernel filename.
	    # -b, -c, -no-emul-boot, -boot-load-size, -boot-info-table
	    #    are options given in the isolinux docs on how to call
	    #    mkisofs.
            mkisocmd = mkisocmd + ' -full-iso9660-filenames -b boot/isolinux/isolinux.bin -c boot/isolinux/boot.cat -no-emul-boot '
            mkisocmd = mkisocmd + '-boot-load-size 4 -boot-info-table '
        if os.path.exists(tidir + '/' + cd):
          for installdir in os.listdir(tidir + '/' + cd):
            mkisocmd = mkisocmd + installdir + '/=' + tidir + '/' + cd + '/' + installdir + '/ '
      elif cdtype == 'lsps':
        if os.path.exists(lidir + '/' + cd):
          for installdir in os.listdir(lidir + '/' + cd):
            mkisocmd = mkisocmd + installdir + '/=' + lidir + '/' + cd + '/' + installdir + '/ '
        if product == 'proasync':
          mkisocmd = mkisocmd + 'host/common/optional/=' + cpdir + '/host/common/optional/ '
      mkisocmd = mkisocmd + cd + '/' + cdtype + '/=' + cpdir + '/' + cd + '/' + cdtype + '/ '
      print 'creating the ' + cdtype + '-' + cd + ' cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
      sys.__stdout__.flush()
      if product not in ('proasync','cgeasync','mobiasync'):
        isoThrds.append(threading.Thread(target=targetIsoThrd, args=(buildtag,buildid,cdtempdir,mkisocmd,cdtype,cddir,logdir,cd)))
      else:
        if not os.path.exists('%s/%s/README.md5sum' % (cddir,cd)):
          if not os.path.exists(cddir + '/' + cd):
            os.system('mkdir -p %s/%s' % (cddir,cd))
          r_md5sum = getResource(buildtag,buildid,"md5sum","Adding md5sum to README.md5sum")
          os.system('cp -a %s/README.md5sum %s/%s' % (cddir,cddir,cd))
          releaseResource(r_md5sum)
        isoThrds.append(threading.Thread(target=targetIsoThrd,args=(buildtag,buildid,cdtempdir,mkisocmd,cdtype,cddir+'/'+cd,logdir,cd)))

    #Above sets up all the threads, this launches them
    for thread in isoThrds:
      thread.start()
    for thread in isoThrds:
      thread.join()
    for cd in cd_targets:
      if cd in abitargets:
        continue
      if os.path.exists(logdir + '/' + cdtype + '-' + cd + '-image-done'):
        print "BUILT: " + cdtype + "-" + cd + " cdimage built"
      else:
        print "BUILD ERROR: " + cdtype + "-" + cd + " cdimage did not build."
      sys.__stdout__.flush()
#------------------------------------------------------------------------------------------
# Creat async lsp iso images for async builds
#------------------------------------------------------------------------------------------
if lspIsos:
  for target in lspIsos.keys():
    isoThrds= []
    print 'creating the async lsp cdimages for ' + target + ' at ' + gettime() + '...'
    sys.__stdout__.flush()
    for lsp in lspIsos[target]:
      mkisocmd = mkisofscmd + '-V ' + lsp
      mkisocmd = mkisocmd + ' -o lsps-' + lsp + '-' + buildid + '.iso '
      mkisocmd = mkisocmd + '-x cluster -x adk -x testing -graft-points '
      print "mkisocmd:"
      print mkisocmd
      sys.__stdout__.flush()
      if os.path.exists(lidir + '/' + target):
        for installdir in os.listdir(lidir + '/' + target):
          mkisocmd = mkisocmd + installdir + '/=' + lidir + '/' + target + '/' + installdir + '/ '
      if product in ('proasync','mobiasync','cgeasync'):
        mkisocmd = mkisocmd + 'host/common/optional/=' + cpdir + '/host/common/optional/ '
        for srcrpm in os.listdir(cpdir + '/SRPMS'):
          if string.find(srcrpm,'host-kernel') > -1:
            mkisocmd = mkisocmd + 'SRPMS/' + srcrpm + '=' + cpdir + '/SRPMS/' + srcrpm + ' '
      mkisocmd = mkisocmd + target + '/lsps/' + lsp + '/=' + cpdir + '/' + target + '/lsps/' + lsp + '/ '
      print 'creating thread for the async lsp cdimage for ' + target + ' ' + buildid + ' at ' + gettime() + '...'
      sys.__stdout__.flush()
      isoThrds.append(threading.Thread(target=targetIsoThrd,args=(buildtag,buildid,cdtempdir,mkisocmd,'lsps',cddir+'/'+target,logdir,lsp+'-'+target)))
    for thrd in isoThrds:
      thrd.start()
    for thrd in isoThrds:
      thrd.join()
    for lsp in lspIsos[target]:
      if os.path.exists(logdir + '/lsps-' + lsp + '-' + target + '-image-done'):
        if string.find(lsp,target) > -1:
          print "BUILT: lsps-" + lsp + " cdimage built"
        else:
          print "BUILT: lsps-" + lsp + "-" + target + " cdimage built"
      else:
        if string.find(lsp,target) > -1:
          print "BUILD ERROR: lsps-" + lsp + " cdimage did not build."
        else:
          print "BUILD ERROR: lsps-" + lsp + "-" + target + " cdimage did not build."
      sys.__stdout__.flush()
#------------------------------------------------------------------------------------------
# Now let's create the dvd images (host, cross, target)
#------------------------------------------------------------------------------------------
if mkdvd:
  isoThrds = []
  print 'creating the dvd images for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
  sys.__stdout__.flush()
  # make dvd images
  dvd_targets = all_targets
  for dvd_target in dvd_targets:
    if dvd_target in abitargets or string.find(dvd_target,'uclibc') > -1:
      continue
    mkisocmd = mkisofscmd + '-V ' + dvdname + '-' + dvd_target + ' -o ' + dvdname + '-' + dvd_target + '-' + buildid + '.iso '
    mkisocmd = mkisocmd + '-x cluster -x testing -x lsps -x done '
    mkisocmd = mkisocmd + '-graft-points '
    xclude = []
    xcludedirs = ['host/common',dvd_target + '/cross/common']
    if dvd_target + '_uclibc' in all_targets:
      xcludedirs.append(dvd_target+'_uclibc/cross/common')
    for host in hosts:
      xcludedirs.append('host/' + host)
      xcludedirs.append(dvd_target+'/cross/' + host)
      if dvd_target + '_uclibc' in all_targets:
        xcludedirs.append(dvd_target+'_uclibc/cross/' + host)
    for chroothost in chroothosts:
      xcludedirs.append('host/' + chroothost)
      xcludedirs.append(dvd_target+'/cross/' + chroothost)
      if dvd_target + '_uclibc' in all_targets:
        xcludedirs.append(dvd_target+'_uclibc/cross/' + chroothost)
    xcludedirs.append(dvd_target+'/target')
    xcludedirs.append(dvd_target+'/target/optional')
    if dvd_target + '_uclibc' in all_targets:
      xcludedirs.append(dvd_target+'_uclibc/target')
      xcludedirs.append(dvd_target+'_uclibc/target/optional')
    os.chdir(cpdir)
    for dir in xcludedirs:
      if os.path.exists(cpdir + '/' + dir):
        os.chdir(cpdir + '/' + dir)
        contents = os.listdir('.')
        for c in contents:
          for o in outtakes:
            if string.find(string.strip(c),o + '-') > -1:
              if string.strip(c) not in xclude:
                xclude.append(string.strip(c))
        if string.find(dir,"uclibc") > -1:
          for c in contents:
            for o in uclibc_outtakes:
              if string.find(string.strip(c),o + '-') > -1:
                if string.strip(c) not in xclude:
                  xclude.append(string.strip(c))
    for x in xclude:
      mkisocmd = mkisocmd + '-x ' + x + ' '
    # copy various install directories into a dvd install directory
    if not os.path.exists(dvdidir + '/' + dvd_target):
      os.system('mkdir -p %s/%s' % (dvdidir,dvd_target))
    # host install directories
    if os.path.exists(hidir):
      os.system('sudo cp -a %s/* %s/%s' % (hidir,dvdidir,dvd_target))
    # cross install directory
    if os.path.exists('%s/%s' % (cidir,dvd_target)):
      os.system('sudo cp -a %s/%s/* %s/%s' % (cidir,dvd_target,dvdidir,dvd_target))
    if dvd_target + '_uclibc' in all_targets:
      if os.path.exists('%s/%s_uclibc' % (cidir,dvd_target)):
        os.system('sudo cp -a %s/%s_uclibc/* %s/%s' % (cidir,dvd_target,dvdidir,dvd_target))
    # target install directories
    if os.path.exists(tidir + '/' + dvd_target):
      os.system('sudo cp -a %s/%s/* %s/%s' % (tidir,dvd_target,dvdidir,dvd_target))
    if dvd_target + '_uclibc' in all_targets:
      if os.path.exists(tidir + '/' + dvd_target + '_uclibc'):
        os.system('sudo cp -a %s/%s_uclibc/* %s/%s' % (tidir,dvd_target,dvdidir,dvd_target))

    # self hosted target directories
    if string.find(dvd_target,'x86') > -1:
      if os.path.exists(shidir + '/' + dvd_target + '/boot/isolinux/isolinux.bin'):
        # Here are the options to enable isolinux native CD-ROM boot
        # -l means allow long (up to 31 chars) iso9660 names for
        #    the kernel filename.
        # -b, -c, -no-emul-boot, -boot-load-size, -boot-info-table
        #    are options given in the isolinux docs on how to call
        #    mkisofs.
        mkisocmd = mkisocmd + ' -full-iso9660-filenames -b boot/isolinux/isolinux.bin -c boot/isolinux/boot.cat -no-emul-boot '
        mkisocmd = mkisocmd + '-boot-load-size 4 -boot-info-table '

    # now include install directory on dvd
    for installdir in os.listdir(dvdidir + '/' + dvd_target):
      if os.path.isdir(dvdidir + '/' + dvd_target + '/' + installdir):
        mkisocmd = mkisocmd + installdir + '/=' + dvdidir + '/' + dvd_target + '/' + installdir + '/ '
      else:
        mkisocmd = mkisocmd + installdir + '=' + dvdidir + '/' + dvd_target + '/' + installdir + ' '

    mkisocmd = mkisocmd + 'host/=' + cpdir + '/host/ '
    mkisocmd = mkisocmd + dvd_target + '/=' + cpdir + '/' + dvd_target + '/ '
    if dvd_target + '_uclibc' in all_targets:
      mkisocmd = mkisocmd + dvd_target + '_uclibc/=' + cpdir + '/' + dvd_target + '_uclibc/ '
    if 'windows2000' in hosts:
      if os.path.exists(cpdir + '/autorun.inf'):
        mkisocmd = mkisocmd + 'autorun.inf=' + cpdir + '/autorun.inf '
      if os.path.exists(cpdir + '/mvista.ico'):
        mkisocmd = mkisocmd + 'mvista.ico=' + cpdir + '/mvista.ico '
    if os.path.exists(cpdir + '/host-tools'):
      mkisocmd = mkisocmd + 'host-tools/=' + cpdir + '/host-tools/ '
    mkisocmd = 'sudo ' + mkisocmd
    print 'creating the ' + dvd_target + ' dvd image for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
    #print 'mkisocmd: ' + mkisocmd
    sys.__stdout__.flush()
    isoThrds.append(threading.Thread(target=targetIsoThrd, args=(buildtag,buildid,cdtempdir,mkisocmd,dvdname,dvddir,logdir,dvd_target)))

  #Above sets up all the threads, this launches them
  for thread in isoThrds:
    thread.start()
  for thread in isoThrds:
    thread.join()
  for dvd in dvd_targets:
    if dvd in abitargets or string.find(dvd,'uclibc') > -1:
      continue
    if os.path.exists(logdir + '/' + dvdname + '-' + dvd + '-image-done'):
      print "BUILT: " + dvdname + "-" + dvd + " cdimage built"
    else:
      print "BUILD ERROR: " + dvdname + "-" + dvd + " image did not build."
    sys.__stdout__.flush()

#-----------------------------------------------------------------------------------------
# make src cd
#-----------------------------------------------------------------------------------------
if mksrccd:
  print 'creating the source cdimage for ' + edition + ' ' + buildid + ' at ' + gettime() + '...'
  sys.__stdout__.flush()
  mkisocmd = mkisofscmd + '-V source -o src-' + edition + '-' + buildid + '.iso '
  mkisocmd = mkisocmd + '-x cluster -x done -x testing '
  xclude = []
  os.chdir(cpdir + '/SRPMS')
  contents = os.listdir('.')
  for c in contents:
    for o in outtakes:
      if string.find(string.strip(c),o + '-') != -1:
        xclude.append(string.strip(c))
    for so in srcouttakes:
      if string.find(string.strip(c),so + '-') != -1:
        xclude.append(string.strip(c))
    for targdir in lspouttakes.keys():
      for dir in lspouttakes[targdir]:
        if string.find(string.strip(c),dir) != -1:
          xclude.append(string.strip(c))
  for x in xclude:
    mkisocmd = mkisocmd + '-x ' + x + ' '
  mkisocmd = mkisocmd + '-graft-points '
  mkisocmd = mkisocmd + 'SRPMS/=' + cpdir + '/SRPMS/ '
  if os.path.exists(cpdir + '/host-tools/windows2000/SRPMS'):
    mkisocmd = mkisocmd + 'host-tools/windows2000/SRPMS/=' + cpdir + '/host-tools/windows2000/SRPMS/ '
  makeIso(buildtag,buildid,cdtempdir,mkisocmd,'src',cddir,logdir,product)
  if os.path.exists(cddir + '/src-' + edition + '-' + buildid + '.iso'):
    print "BUILT: source cdimage built"
  else:
    print "BUILD ERROR: source cdimage did not build."
  sys.__stdout__.flush()

#------------------------------------------------------------------------------------------
# Now let's create the doc cdimage
#------------------------------------------------------------------------------------------
if mkdoccd:
  print '<' + sys.argv[0] + '>: checking for the docs-cd installer for ' + sys.argv[1] + ' ' + buildid + ' at ' + gettime() + '...'
  sys.__stdout__.flush()
  # check for docs-cd-installer rpms
  hf = string.strip(os.popen('ls ' + installrpmdir + '/docs-cd/docs-cd-installer*').read())
  if not os.path.exists(hf):
    print 'docs-cd-installer.mvl does not exist ... skipping'
    sys.__stdout__.flush()
    print "BUILD ERROR: doc cdimage did not build."
    sys.__stdout__.flush()
  #if it's there let's install it
  else:
    print 'installing docs-cd-installer.mvl ...'
    sys.__stdout__.flush()
    rpmdb = getResource(buildtag,buildid,"dumborpmdb","Installing installer rpms")
    os.system('rpm --dbpath /tmp/rpmdb -ihv  ' + installrpmdir + 
              '/docs-cd/docs-cd-installer*.mvl --prefix ' +
              didir + ' --nodeps --force --ignoreos --ignorearch')
    releaseResource(rpmdb)
    sys.__stdout__.flush()
                                                                                                                # Change the volume file for the hostcd
    os.chdir(iadir + '/docs-cd' + voldir)
    contents = os.listdir('.')
    for c in contents:
      print 'For ' + c + ' moving ' + old + ' to ' + new + ' ...'
      os.system('mv ' + c + ' ' + string.replace(c,old,new))
      sys.__stdout__.flush()
    # Copy the installed components to cpdir for NFS installs
    os.system('cp -a ' + didir + '/* ' + cpdir)

    print 'creating the docs cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
    sys.__stdout__.flush()
    cd = 'docs'
    mkisocmd = mkisofscmd + '-V ' + cd + ' -o ' + cd + '-' + edition + '-' + buildid + '.iso '
    mkisocmd = mkisocmd + '-x CVS '
    mkisocmd = mkisocmd + '-graft-points '
    for gp in docsgp.keys():
      if os.path.exists(cpdir + '/' + string.strip(docsgp[gp])):
        mkisocmd = mkisocmd + gp + '=' + cpdir + '/' + docsgp[gp]
    for installdir in os.listdir(didir):
      if os.path.isdir(didir + '/' + installdir):
        mkisocmd = mkisocmd + installdir + '/=' + didir + '/' + installdir + '/ '
    makeIso(buildtag,buildid,cdtempdir,mkisocmd,'docs',cddir,logdir,product)
    if os.path.exists(logdir + '/docs-image-done'):
      print "BUILT: doc cdimage built"
    else:
      print "BUILD ERROR: doc cdimage did not build."
  os.chdir(builddir)
# comment this next block since docs cds are no longer required for install...
# once this is verified, delete this block of code
#else:
#  print 'creating the dummy doc cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
#  sys.__stdout__.flush()
#  cd = 'docs'
#  for b in body:
#    os.system('echo "' + b + '" >> %s/README-doc' %(cpdir))
#  mkisocmd = mkisofscmd + '-V ' + cd + ' -o ' + cd + '-' + product + '-' + buildid + '.iso '
#  mkisocmd = mkisocmd + '-x CVS '
#  mkisocmd = mkisocmd + '-graft-points '
#  mkisocmd = mkisocmd + 'README=' + cpdir + '/README-doc '
#  makeIso(buildtag,buildid,cdtempdir,mkisocmd,'docs',cddir,logdir,product)
#  if os.path.exists(logdir + '/docs-image-done'):
#    print "BUILT: dummy doc cdimage built"
#  else:
#    print "BUILD ERROR: dummy doc cdimage did not build."
#  os.chdir(builddir)
  
#------------------------------------------------------------------------------------------
  print 'Finished creating the doc cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
sys.__stdout__.flush()
#-------------------------------------------------------------------------------------------
# make the boms of the cds
#-------------------------------------------------------------------------------------------
if mkcdbom:
  os.chdir(builddir)
  print 'creating the cd boms for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
  sys.__stdout__.flush()
  os.system('./bommaker.py %s %s %s' % (product,buildtag,cddir))
  print 'cd bommaker finished at ' + gettime()
  sys.__stdout__.flush()
  if mkdvd:
    print 'creating the dvd boms for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
    sys.__stdout__.flush()
    os.system('./bommaker.py %s %s %s' % (product,buildtag,dvddir))
    print 'dvd bommaker finished at ' + gettime()
    sys.__stdout__.flush()
#-------------------------------------------------------------------------------------------
# make links to docs, src and lsp cd isos in dvd images directory, adn add md5sums
#-------------------------------------------------------------------------------------------
if mkdvd:
  os.chdir(cddir)
  lspisos = os.popen('ls lsps*.iso').readlines()
  os.chdir(dvddir)
  print 'Linking lsp,src and docs isos to dvdimages at ' + gettime() + '...'
  for lspiso in lspisos:
    os.system('ln %s/%s .' % (cddir,string.strip(lspiso)))
  os.system('ln %s/src* .' % cddir)
  os.system('ln %s/doc* .' % cddir)
  print 'Adding lsp,src and docs md5sums to dvdimages/README.md5sum at ' + gettime() + '...'
  r_md5sum = getResource(buildtag,buildid,"md5sum","Adding md5sum to README.md5sum")
  md5sums = os.popen('cat %s/README.md5sum' % cddir).readlines()
  f_md5sum = open('%s/README.md5sum' % dvddir,'a')
  for md5sum in md5sums:
    if string.find(md5sum,'lsps-') > -1 or string.find(md5sum,'doc') > -1 or string.find(md5sum,'src') > -1:
      f_md5sum.write(md5sum)
  f_md5sum.close()
  releaseResource(r_md5sum)
  os.system('cp -a %s/BOMS/* %s/BOMS' % (cddir,dvddir))
#-------------------------------------------------------------------------------------------
#Generate the version tables
#-------------------------------------------------------------------------------------------
if mkvert:
  os.chdir(builddir)
  print 'Generating the versiontable for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
  sys.__stdout__.flush()
  if product in ('dev','foundation'):
    os.system('./versiontable.py -a -l -d %s/ ' % cpdir)
  else:
    os.system('./versiontable.py -a -l -d %s/ -b %s/BOMS/ ' % (cpdir,dvddir))
  print 'Version table finished at ' + gettime()
  sys.__stdout__.flush()

os.system('rm -rf ' + cdtempdir)
print 'installimage is done'
