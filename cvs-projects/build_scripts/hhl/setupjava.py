#!/usr/bin/python
import sys, os, string, re, getopt, time

# arg 1 = build_id
# arg 2 = product (pe,cge,cee,etc)

build_id = sys.argv[1]
product = sys.argv[2]

buildData = os.getcwd() + '/buildData.dat'
scriptpath = os.getcwd()
conf = open(buildData)
exec(conf)

apps = '*g++* *gcc* *glibc* *kernel-headers* *libjpeg* *libltdl* *c++* *libtool* *zlib*'

if product == 'pe' or product == 'xtensa':
  instdir = '/opt/montavista'
elif product == 'cee':
  instdir = '/opt/montavista'
elif product == 'cge':
  instdir = '/opt/montavista'
rpmdb = instdir + '/rpmdb'

# clean rpmdb
os.system('rm -rf ' + instdir + '/*')
os.system('cp -a /var/lib/rpm ' + rpmdb)

# install all archs from /mvista/dev_area/<build_id>
os.chdir('/mvista/dev_area/' + build_id)
os.system('echo "I am in `pwd`"')
# install host stuff
os.chdir('host/common/optional/')
os.system('echo "I am in `pwd`"')
os.system('rpm -ivh *.mvl --dbpath ' + rpmdb)
os.chdir('/mvista/dev_area/' + build_id + '/host/common')
os.system('echo "I am in `pwd`"')
for x in os.listdir('/mvista/dev_area/' + build_id + '/host/common'):
  if string.find(x,'hhl_install') == -1 and not os.path.isdir(x):
    os.system('rpm -ivh ' + x + ' --dbpath ' + rpmdb)
os.chdir('/mvista/dev_area/' + build_id + '/host/redhat72/')
os.system('echo "I am in `pwd`"')
os.system('rpm -ivh *.mvl  --dbpath ' + rpmdb)

for arch in os.listdir('/mvista/dev_area/' + build_id):
  # check to see if directory is an arch
  if os.path.exists(arch + '/cross'):
    os.system('rpm -ivh ' + arch + '/cross/common/* --force --dbpath ' + rpmdb)
    os.system('rpm -ivh ' + arch + '/cross/redhat72/* --force --dbpath ' + rpmdb)
  if os.path.exists(arch + '/target'):
    os.chdir('/mvista/dev_area/' + build_id + '/' + arch + '/target')
    os.system('echo "I am in `pwd`"')
    os.system('rpm -ivh --ignorearch ' + apps + ' --dbpath ' + rpmdb)
  os.chdir('/mvista/dev_area/' + build_id)
# query database for all hhl rpms to verify everything is installed
os.system('rpm -qa | grep hhl')

