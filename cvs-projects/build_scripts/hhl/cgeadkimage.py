#!/usr/bin/python
import sys, os, string, re, getopt, time

# cgeadkimage.py

# This script installs the host installer, creates the host cdimage
# It then installs the target installer and creates the target cdimage(s)
# if you only want one type, i.e host|target you set this in <product>data.dat
# if you don't want to create all of your editions target cds you can set arch to which
# target you want the installer and cdimage(s) created for in <product>data.dat.


if len(sys.argv) == 1:
  print 'usage: %s %s %s %s' % (sys.argv[0],'<cpdir>','<buildid>','<buildtag>')
  sys.exit(1)

cpdir = sys.argv[1]
print 'cpdir = ' + cpdir
buildid = sys.argv[2]
print 'buildid = ' + buildid
buildtag = sys.argv[3]
print 'buildtag = ' + buildtag
header = [ "The following information is the MD5 checksums of each file",
          "contained in this directory.  This information is used to",
          "verify that the files downloaded from this directory were not",
          "corrupted during the transfer.",
          " ",
          "            md5sum                          file",
          "--------------------------------  ---------------------------"]

#------------------------------------------------------------------------------------------
# 
#------------------------------------------------------------------------------------------
def gettime():
  t_time = time.localtime(time.time())
  s_time = time.strftime("%H:%M:%S %Z",t_time)
  f_time = time.mktime(t_time)
  return s_time + ' [' + str(f_time) + ']'

#------------------------------------------------------------------------------------------
# Read <product>data.dat 
#------------------------------------------------------------------------------------------
builddir = os.getcwd()
product = 'cgeadk'
# get nodes, hosts and bfnode from /home/build/bin/nodelist.py
exec(open('/home/build/bin/nodelist.py'))
exec(open(builddir + '/cgeadkdata.dat'))

# generate cdnodes from nodes (from nodelist.py) and all_targets (from conf file)
n = 0
numnodes = len(nodes)
print 'nodes:'
print nodes
print 'all_targets:'
print all_targets
cdnodes = {}
for a in all_targets:
  cdnodes[a] = nodes[n]
  n=n+1
  if n == numnodes:
    n = 0

#volume file stuff:
old = ('-00000')
new = ('-00001')

cddir = '/mvista/dev_area/cge/cdimages/adk/' + buildtag
print 'cddir = ' + cddir
os.system('mkdir -p ' + cddir)
# make a temporary cd directory to build cdimages locally, rather than
# on dumbo, then copy images to dumbo
cdtempdir = '/var/tmp/CDTEMP'
os.system('mkdir -p ' + cdtempdir)
installrpmdir = cpdir + '/installer_rpms'
iadir = installrpmdir + '/install_area'
voldir = '/etc/config/volume'
#shidir = installrpmdir + '/install_area/self-hosted'
#print 'self_hosted_installdir = ' + shidir
cidir = installrpmdir + '/install_area/cross'
print 'cross_installdir = ' + cidir
tidir = installrpmdir + '/install_area/target'
print 'target_installdir = ' + tidir
hidir = installrpmdir + '/install_area/host'
print 'host_installdir = ' + hidir
os.chdir(cddir)
for h in header:
    os.system('echo "' + h + '" >> README.md5sum')
os.chdir(builddir)
logdir = '/mvista/dev_area/cge/adk/' + buildtag

cdhosts = chroothosts.keys()
for host in hosts.keys():
  cdhosts.append(host)
#------------------------------------------------------------------------------------------
if hostcdinstall:
  print '<' + sys.argv[0] + '>: checking for the host installer for ' + sys.argv[1] + ' ' + buildid + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
  sys.__stdout__.flush()
#-----------------------------------------------------------------------------------------
# check for host-cd-installer
#------------------------------------------------------------------------------------------
  for h in cdhosts: 
    hf = string.strip(os.popen('ls ' + installrpmdir + '/host/' + h + '/*cd-installer*').read())
    if not os.path.exists(hf):
      print 'host-cd-installer.mvl does not exist for host ' + h + ' ... skipping ' + sys.argv[0] + ' ...'
    #if it's there let's install it
    else:
      print 'installing host-cd-installer.mvl for host ' + h + ' ...'
      sys.__stdout__.flush()
      os.system(rpmbin  + '-forward -ihv ' + installrpmdir + '/host/' +h+ '/host-cd-installer*.mvl --prefix ' + 
                hidir + ' --nodeps --force --ignoreos --ignorearch')
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
  print 'creating the host cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
  sys.__stdout__.flush()
if mkhostcd:
  #make host images
  cd = 'host'
  mkisocmd = 'mkisofs -quiet -r -J -joliet-long -L -no-split-symlink-components -no-split-symlink-fields '
  mkisocmd = mkisocmd + '-V ' + cd + ' -o ' + cd + '-adk-' + buildid + '.iso '
  mkisocmd = mkisocmd + '-x cluster -x done -x SRPMS '
  mkisocmd = mkisocmd + '-graft-points '
  if 'windows2000' in hosts.keys():
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
  for gp in hostdocsgp.keys():
    if os.path.exists(cpdir + '/' + string.strip(hostdocsgp[gp])):
      mkisocmd = mkisocmd + gp + '=' + cpdir + '/' + hostdocsgp[gp]
  os.chdir(cdtempdir)
  print 'mkisocmd: '
  print mkisocmd
  if not os.system(mkisocmd):
    os.system('md5sum ' + cd + '-adk-' + buildid + '.iso > md5sum')
    os.system('mv ' + cdtempdir + '/' + cd + '-adk-' + buildid + '.iso ' +
             cddir)
    os.chdir(cddir)
    os.system('cat ' + cdtempdir + '/md5sum >> README.md5sum')
    print "BUILT: host cdimage built"
  else:
    print "BUILD ERROR: host cdimage did not build."
  os.chdir(builddir)
#------------------------------------------------------------------------------------------
  print 'Finished creating the host cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
sys.__stdout__.flush()

# -----------------------------------------------------------------------------------------
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
      os.system(rpmbin  + '-forward -ihv  ' + installrpmdir + '/cross/' + target + '/' + tf + 
                ' --prefix ' + cidir + '/' + target + ' --ignorearch --nodeps --force')

  # install all arch-cd-installer rpms from installer_rpm/target/<target>
  for target in os.listdir(installrpmdir + '/target'):
    os.chdir(installrpmdir + '/target/' + target)
    tf = string.strip(os.popen('ls *cd-install*').read())
    os.chdir(builddir)
    if not os.path.isfile(installrpmdir + '/target/' + target + '/' + tf):
      print tf + ' does not exist for build ' + product + ' ' + buildid + ' ... skipping arch-cd-installer...'
    #if it's there let's install it
    else:
      os.system(rpmbin  + '-forward -ihv  ' + installrpmdir + '/target/' + target + '/' + tf + ' --prefix ' + tidir + '/' + target + ' --ignorearch --nodeps --force')

    # Change the volume file for cross/target cd
    vdirs = [cidir, tidir]
    for vd in vdirs:
      if os.path.exists(vd + '/' + target + voldir):
        os.chdir(vd + '/' + target + voldir)
        contents = os.listdir('.')
        for c in contents:
          print 'For ' + c + ' moving ' + old + ' to ' + new + ' ...'
          os.system('mv ' + c + ' ' + string.replace(c,old,new))
          sys.__stdout__.flush()
      # copy target installers for NFS installs
      for target in os.listdir(vd):
        os.system('cp -a ' + vd + '/' + target + '/* ' + cpdir)
      # copy the x86_pentium2 cross/target install files into each arch cross/target install area
      for target in os.listdir(vd):
        os.system('cp -a ' + vd + '/x86_pentium2/* ' + vd + '/' + target)

  # install self-hosted-installer rpms from installer_rpms/self-hosted/<target>
  #if installtarget != 'null':
  #  os.chdir(installrpmdir + '/self-hosted/' + installtarget)
  #  tf = string.strip(os.popen('ls *self-hosted*').read())
  #  os.chdir(builddir)
  #  if not os.path.isfile(installrpmdir + '/self-hosted/' + installtarget + '/' + tf):
  #    print tf + ' does not exist for build ' + product + ' ' + buildid + ' ... skipping self-hosted-installer...'
  #    sys.__stdout__.flush()
  #  else:
  #    os.system(rpmbin  + '-forward -ihv  ' + installrpmdir + '/self-hosted/' + installtarget + '/' + tf + ' --prefix ' + shidir + '/' + installtarget + ' --ignorearch --nodeps --force')
  #    sys.__stdout__.flush()

      # install generic-hhl_install lsp
  #    if os.path.exists(cpdir + '/' + installtarget + '/lsps/generic_x86-hhl_install/target'):
  #      os.chdir(cpdir + '/' + installtarget + '/lsps/generic_x86-hhl_install/target')
  #      tlspf = string.strip(os.popen('ls *.mvl').read())
  #      os.chdir(builddir)
  #      if not os.path.isfile(cpdir + '/' + installtarget + '/lsps/generic_x86-hhl_install/target/' + tlspf):
  #        print tlspf + ' does not exist for build ' + product + ' ' + buildid + ' ... skipping bootflop.img...'
  #        sys.__stdout__.flush()
  #      else:
  #        os.system('sudo ' + rpmbin  + '-forward -ihv  ' + cpdir + '/' + installtarget + 
  #                  '/lsps/generic_x86-hhl_install/target/lsp*.mvl  --prefix '
  #                  + shidir + '/' + installtarget + ' --ignorearch --nodeps --force ')
  #        sys.__stdout__.flush()
  #        # make bootfloppy image
  #        if bfnode != "null":
  #          os.system('ssh %s "cd %s; ./mkbootflop.py %s %s %s %s %s %s %s"' % (bfnode,builddir,cpdir,
  #                     installtarget,kernelinfo,hhldist,rpmbin,shidir,version))
  #        else:
  #          print '\nbfnode = null, skipping mkbootflop.py...you may want to check nodelist.py\n'
  #        sys.__stdout__.flush()
  #        print 'mkbooflop.py finished at ' + gettime()
  #        sys.__stdout__.flush()
  #        # now copy all self-hosted/target directories to all cross/<target> directories (x86 only) and
  #        # this may|may not change for new cd structure.  gay.
  #        for targetdir in os.listdir(tidir):
  #          if string.find(targetdir,'x86') > -1:
  #            os.system('cp -a ' + shidir + '/' + installtarget + '/* ' + tidir + '/' + targetdir)
  sys.__stdout__.flush()
  #------------------------------------------------------------------------------------------
  # Now let's create the target cdimages (cross, target, lsp)
  #------------------------------------------------------------------------------------------
if mktargetcd:
  for cdtype in cdnames:
    print 'creating the ' + cdtype + ' cdimages for ' + product + ' ' + buildid + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
    sys.__stdout__.flush()
    #make target images
    #print 'all_targets:'
    #print all_targets
    if cdtype == 'cross':
      vd = cidir
    elif cdtype == 'target':
      vd = tidir
    for cd in all_targets:
      mkisocmd = 'mkisofs -quiet -r -J -joliet-long -L -no-split-symlink-components -no-split-symlink-fields '
      mkisocmd = mkisocmd + '-V ' + cdtype + '-' + cd + ' -o ' + cdtype + '-' + cd + '-adk-' + buildid + '.iso '
      mkisocmd = mkisocmd + '-x cluster '
      mkisocmd = mkisocmd + '-graft-points '
      for installdir in os.listdir(vd + '/' + cd):
        mkisocmd = mkisocmd + installdir + '/=' + vd + '/' + cd + '/' + installdir + '/ '
        #if string.find(cd,'x86') > -1:
        #  if os.path.exists(shidir + '/' + installtarget + '/bootimg/bootflop.img'):
        #    mkisocmd = mkisocmd + '-b bootimg/bootflop.img -c boot.catalog '
      mkisocmd = mkisocmd + cd + '/' + cdtype + '/=' + cpdir + '/' + cd + '/' + cdtype + '/ '
      if cd != 'x86_pentium2':
        mkisocmd = mkisocmd + 'x86_pentium2/' + cdtype + '/=' + cpdir + '/x86_pentium2/' + cdtype + '/ '
        #mkisocmd = mkisocmd + 'x86_pentium2/target/=' + cpdir + '/x86_pentium2/target/ '
      for gp in docsgp.keys():
        if os.path.exists(cpdir + '/' + string.strip(docsgp[gp])):
          mkisocmd = mkisocmd + gp + '=' + cpdir + '/' + docsgp[gp]
      print 'creating the ' + cdtype + '-' + cd + ' cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + ' on: ' + cdnodes[cd] + '...'
      sys.__stdout__.flush()
      os.system('ssh ' + cdnodes[cd] + ' "mkdir -p ' + cdtempdir + '; ' +
             'cd ' + cdtempdir + '; ' + mkisocmd + '; ' +
             'md5sum ' + cdtype + '-' + cd + '-adk-' + buildid + '.iso > md5sum; ' +
             'mv ' + cdtempdir + '/' + cdtype + '-' + cd + '-adk-' + buildid + '.iso ' + cddir + '; ' +
             'cat md5sum >> ' + cddir + '/README.md5sum; ' +
             'touch ' + logdir + '/' + cdtype + '-' + cd + '-image-done" &')
      sys.__stdout__.flush()
    #-----------------------------------------------------------------------------------------
    # loop to check for all -image-done files
    #-----------------------------------------------------------------------------------------
    cdarchs = []
    for a in all_targets:
      cdarchs.append(a)
    while len(cdarchs) > 0:
      for cd in cdarchs:
        if os.path.exists(logdir + '/' + cdtype + '-' + cd + '-image-done'):
          cdarchs.remove(cd)
          print 'Finished creating ' + cdtype + '-' + cd + ' cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + ' on: ' + cdnodes[cd] + '...'
          if os.path.exists(cddir + '/' + cdtype + '-' + cd + '-adk-' + buildid + '.iso'):
            print 'BUILT: ' + cdtype + '-' + cd + ' cdimage built'
          else:
            print 'BUILD ERROR: ' + cdtype + '-' + cd + ' cdimage did not build'
          sys.__stdout__.flush()

#-----------------------------------------------------------------------------------------
# make src cd
#-----------------------------------------------------------------------------------------
if mksrccd:
  print 'creating the source cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
  sys.__stdout__.flush()
  mkisocmd = 'mkisofs -quiet -r -J -joliet-long -L -no-split-symlink-components -no-split-symlink-fields '
  mkisocmd = mkisocmd + '-V source -o src-adk-' + buildid + '.iso '
  mkisocmd = mkisocmd + '-x cluster -x done '
  mkisocmd = mkisocmd + '-graft-points '
  mkisocmd = mkisocmd + 'SRPMS/=' + cpdir + '/SRPMS/ '
  if os.path.exists(cpdir + '/host-tools/windows2000/SRPMS'):
    mkisocmd = mkisocmd + 'host-tools/windows2000/SRPMS/=' + cpdir + '/host-tools/windows2000/SRPMS/ '
  os.chdir(cdtempdir)
  os.system(mkisocmd + '; md5sum src-adk-' + buildid + '.iso > md5sum; mv ' + cdtempdir + 
            '/src-adk-' + buildid + '.iso ' + cddir + '; cd ' + cddir + '; cat ' + cdtempdir + 
            '/md5sum >> README.md5sum')
  if os.path.exists(cddir + '/src-adk-' + buildid + '.iso'):
    print "BUILT: source cdimage built"
  else:
    print "BUILD ERROR: source cdimage did not build."
  sys.__stdout__.flush()

if mkcdbom:
  os.chdir(builddir)
  print 'creating the boms for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
  sys.__stdout__.flush()
  os.system('./bommaker.py %s %s' % ('cge','adk/'+ buildtag))
  sys.__stdout__.flush()
  print 'bommaker finished at ' + gettime()
  sys.__stdout__.flush()
  
print 'installimage is done'
