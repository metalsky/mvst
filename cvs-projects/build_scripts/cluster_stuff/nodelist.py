#!/usr/bin/python
import string

global hosts, nodes

hosts = {}
nodes = []
bfnode = "null"
####################
# foundation builds:
####################
if product == 'scripttest':
  hosts = { 
     'windows2000': (['cygwin-1',], 'buildcygwin', '/home/build/dailybuild'),
     'solaris8': (['solaris8-11',], 'buildremote.py', '/home/build')
	}
  nodes = string.split('node-3 node-4', ' ')
  bfnode = 'node-4'

elif product in ('dev','devstaging'):
  hosts = {
     'windows2000': (['cygwin-1','cygwin-2','cygwin-3','cygwin-4','cygwin-5','cygwin-6','cygwin-8','cygwin-9','cygwin-10','cygwin-11'], 'buildcygwin', '/home/build/dailybuild'),
     'solaris8': (['solaris8-8','solaris8-9','solaris8-3','solaris8-4','solaris8-5','solaris8-6','solaris8-7','solaris8-1','solaris8-2'], 'buildsparc', '/home/build')
          }
  nodes = string.split('node-9 node-10 node-11 node-12 node-13 node-14 node-15 node-16 node-17 node-18 node-19 node-20 node-21 node-22 node-23 node-24 node-25 node-26 node-27 node-28 node-29 node-30 node-31 node-32 node-33 node-34 node-35 node-36 node-37 node-38 node-39 node-40 node-41 node-42', ' ')
  bfnode = 'node-18'

elif product in ('stb',):
  hosts = {
     #'windows2000': (['cygwin-9',], 'buildcygwin', '/home/build/dailybuild'),
     #'solaris8': (['solaris8-8','solaris8-9','solaris8-4','solaris8-5','solaris8-6','solaris8-7','solaris8-1','solaris8-2'], 'buildsparc', '/home/build')
          }
  nodes = string.split('node-4 node-5', ' ')
  bfnode = 'node-18'

elif product == 'fe':
  hosts = {
     'solaris8': (['solaris8-8','solaris8-9','solaris8-3','solaris8-4','solaris8-5','solaris8-6','solaris8-7','solaris8-1','solaris8-2'],
                    'buildsparc', '/opt/dailybuild'),
     'windows2000': (['cygwin-1','cygwin-2','cygwin-3','cygwin-4','cygwin-5','cygwin-6','cygwin-8','cygwin-9'], 'buildcygwin',
                       '/home/build/dailybuild'),
          }
  nodes = string.split('node-9 node-10 node-11 node-12 node-13 node-14 node-15 node-16 node-17 node-18 node-19 node-20 node-21 node-22 node-23 node-24 node-25 node-26 node-27 node-28 node-29 node-30 node-31 node-32 node-33 node-34 node-35 node-36 node-37 node-38 node-39 node-40 node-41 node-42', ' ')
  bfnode = 'node-18'

elif product == 'fetest':
  hosts = { }
  nodes = string.split('node-3 node-4', ' ')
  bfnode = 'node-3'

elif product == 'fone':
  hosts = {
     'solaris7': (['solaris8-1','solaris8-2','solaris8-3','solaris8-4','solaris8-5','solaris8-6','solaris8-7','solaris8-8'],
                    'buildsparc', '/opt/dailybuild'),
     'windows2000': (['cygwin-1','cygwin-2','cygwin-3','cygwin-4','cygwin-5','cygwin-6','cygwin-8','cygwin-9'], 'buildcygwin',
                       '/home/build/dailybuild'),
          }
  nodes = string.split('node-6 node-7 node-8 node-9 node-10 node-11 node-12 node-13 node-14 node-15 node-16 node-17 node-18 node-19 node-20 node-21 node-22 node-23 node-24 node-25 node-26 node-27 node-28 node-29 node-30 node-31 node-32 node-33 node-34 node-35 node-36 node-37 node-38 node-39 node-40 node-41 node-42', ' ')
  bfnode = 'node-18'

elif product == 'fe64':
  hosts = {
     'solaris7': (['solaris8-1','solaris8-2','solaris8-3','solaris8-4'],
                    'buildsparc', '/opt/dailybuild'),
     'windows2000': (['cygwin-1','cygwin-2','cygwin-3','cygwin-4'], 'buildcygwin',
                       '/home/build/dailybuild'),
          }
  nodes = string.split('node-7 node-8 node-9 node-10', ' ')
  bfnode = 'node-10'

elif product == 'fone_vr':
  hosts = {
     'solaris7': (['solaris8-11'],
                    'buildsparc', '/opt/dailybuild'),
     'windows2000': (['cygwin-7'], 'buildcygwin',
                       '/home/build/dailybuild'),
          }
  nodes = string.split('node-3 node-4', ' ')
  bfnode = 'node-4'

elif product in ('dev64',):
  hosts = { }
  nodes = string.split('node-6 node-7 node-8 node-9 node-10', ' ')
  bfnode = 'node-6'

elif product in ('dev-merge',):
  hosts = { }
  nodes = string.split('node-6 node-7 node-8 node-9 node-11 node-12 node-17 node-18 node-19 node-20 node-21 node-22 node-23 node-24 node-25 node-26 node-27 node-28 node-29 node-30 node-31 node-33 node-34 node-35 node-36 node-37 node-38 node-39 node-40', ' ')
  bfnode = 'node-6'

elif product == 'asyncfe':
  hosts = {
      'windows2000': (['cygwin-5','cygwin-6'], 'buildcygwin',
                       '/home/build/dailybuild'),
      'solaris7': (['solaris8-4','solaris8-5','solaris8-6','solaris8-7'],
                   'buildsparc', '/opt/dailybuild')
          }
  #nodes = string.split('node-16 oldnode-13 oldnode-14', ' ')
  #nodes = string.split('node-6 node-7 node-8 node-9 node-10 node-11 node-12 node-17', ' ')
  nodes = string.split('node-7 node-8 node-9 node-10 node-11 node-12 node-17', ' ')
  bfnode = 'node-6'

elif product == 'asyncthumb':
  hosts = {
      'windows2000':  (['cygwin-4',], 'buildcygwin','/home/build/dailybuild'),
          }
  nodes = string.split('node-16', ' ')
#  nodes = string.split('node-5', ' ')

elif product == 'mips64':
  hosts = {
      'windows2000':  (['cygwin-2',], 'buildcygwin','/home/build/dailybuild'),
      'solaris7':     (['solaris8-5',], 'buildsparc', '/opt/dailybuild')
          }
  nodes           = string.split('node-10 node-11', ' ')

elif product == 'famd64':
  hosts = {
      'solaris7':     (['solaris8-11','solaris8-3'], 'buildsparc', '/opt/dailybuild'),
          }
  #nodes           = string.split('node-2', ' ')
  nodes           = string.split('node-2 node-5', ' ')

elif product == 'fem64t':
  hosts = {
      #'solaris7':     (['solaris8-8',], 'buildsparc', '/opt/dailybuild'),
          }
  nodes           = string.split('node-5', ' ')

elif product == 'mtb':
  hosts = { }
  nodes 	= string.split('node-5', ' ')

################
# eclipse builds
################
elif product == 'feeclipse':		# use for dev eclipse build only, not dev rocket 1.0 for cge
  hosts = {
      'windows2000':  (['cygwin-2',], 'buildcygwin','/home/build/dailybuild'),
      'solaris7':  (['solaris8-3',], 'buildsparc', '/opt/dailybuild'),
          }
  nodes = string.split('node-21 node-22', ' ')	# use for dev rocket 1.1 (pro adk)
  #nodes = string.split('node-13 node-14 node-15 node-17 node-18', ' ')	# use for dev rocket 1.1 (pro adk)

elif product == 'deveclipse':
  hosts = {
      'windows2000':  (['cygwin-3',], 'buildcygwin','/home/build/dailybuild'),
      'solaris7':     (['solaris8-3',], 'buildsparc', '/opt/dailybuild')
          }
  nodes = string.split('node-18 node-17 node-20', ' ')

elif product == 'ceeeclipse':
  hosts = {
      'windows2000':  (['cygwin-4',], 'buildcygwin','/home/build/dailybuild'),
      'solaris7':  (['solaris8-5',], 'buildsparc', '/opt/dailybuild'),
          }
  nodes = string.split('node-16 oldnode-13 oldnode-14', ' ')

elif product == 'proeclipse':
  hosts = {
      'windows2000': (['cygwin-1','cygwin-2','cygwin-3','cygwin-5'], 'buildcygwin','/home/build/dailybuild'),
      'solaris7':    (['solaris8-1','solaris8-2','solaris8-3','solaris8-4','solaris8-5','solaris8-6','solaris8-7'],
                       'buildsparc', '/opt/dailybuild')
          }
  nodes = string.split('node-7 node-8 node-9 node-10 node-11 node-12 node-18 node-19 node-20 node-21 node-22 node-23 node-24 node-25 node-26 node-27 node-28 node-29 node-30 node-31', ' ')

################
# edition builds
################
elif product == 'pro':
  hosts = {
     'windows2000': (['cygwin-3','cygwin-4','cygwin-5','cygwin-6'],
                       'buildcygwin','/home/build/dailybuild'),
     #'solaris8': (['solaris8-1','solaris8-2','solaris8-3','solaris8-4','solaris8-5'],
     'solaris8': (['solaris8-2','solaris8-5'],
                    'buildsparc', '/opt/dailybuild')
          }
  nodes = string.split('node-21 node-22 node-23 node-24 node-25 node-26 node-27 node-28 node-29 node-30 node-31 node-32 node-33 node-34 node-35 node-36 node-37 node-38 node-39 node-40 node-41 node-42',' ')
  bfnode = 'node-21'

elif product == 'prodb':
  hosts = {
      'windows2000': (['cygwin-1','cygwin-2','cygwin-3','cygwin-5'],
                       'buildcygwin','/home/build/dailybuild'),
      'solaris7': (['solaris8-1','solaris8-2','solaris8-3','solaris8-4','solaris8-5','solaris8-6','solaris8-7'],
                    'buildsparc', '/opt/dailybuild')
          }
  nodes = string.split('node-7 node-8 node-9 node-10 node-11 node-12 node-17 node-18 node-19 node-20 node-21 node-22 node-23 node-24 node-25 node-26 node-27 node-28 node-29 node-30 node-31', ' ')
  bfnode = 'node-18'

elif product == 'propk':
  nodes = string.split('node-6 node-7 node-8 node-9 node-10 node-11 node-12 node-17 node-18 node-19 node-20 node-21 node-22 node-23 node-24 node-25 node-26 node-27 node-28 node-29 node-30 node-31', ' ')

elif product == 'proadk':
  hosts = {
      'windows2000': (['cygwin-1','cygwin-2','cygwin-3'], 'buildcygwin','/home/build/dailybuild'),
      'solaris7':    (['solaris8-1','solaris8-2','solaris8-3','solaris8-4','solaris8-5','solaris8-6'],
                       'buildsparc', '/opt/dailybuild')
          }
  nodes = string.split('node-6 node-7 node-8 node-9 node-10 node-11 node-12 node-18 node-19 node-20 node-21 node-22 node-23 node-24 node-25 node-26 node-27 node-28 node-30 node-31', ' ')

elif product == 'proasync':
  hosts = {
      # uncomment for 3.1 or 3.0 pro asyncs
      #'windows2000': (['cygwin-7'], 'buildcygwin',
      #                 '/home/build/dailybuild'),
      #'solaris7': (['solaris8-3',],
      #              'buildsparc', '/opt/dailybuild')
          }
  nodes = string.split('node-3', ' ')
  bfnode = 'node-3'

elif product == 'prom64async':
  hosts = {
      'windows2000':  (['cygwin-5',], 'buildcygwin','/home/build/dailybuild'),
      'solaris7':     (['solaris8-4',], 'buildsparc', '/opt/dailybuild')
          }
  nodes = string.split('node-6', ' ')
  bfnode = 'node-18'

elif product == 'cge':
  hosts = {
      'solaris8':  (['solaris8-6','solaris8-7','solaris8-8','solaris8-9'], 'buildsparc', '/opt/dailybuild'),
          }
  nodes = string.split('node-12 node-13 node-14 node-15 node-16 node-17 node-18 node-19 node-20', ' ')
  #nodes = string.split('node-3', ' ')
  bfnode = 'node-3'

elif product == 'cgeem64':
  hosts = { }
  nodes = string.split('node-2', ' ')
  bfnode = 'node-2'

elif product == 'munich':
  hosts = { }
  nodes = string.split('node-2 node-3', ' ')
  bfnode = 'node-3'

elif product == 'cgeup':
  hosts = {
      'solaris7':  (['solaris8-4',], 'buildsparc', '/opt/dailybuild'),
          }
  nodes = string.split('node-1 node-2 node-4 node-5 oldnode-13 oldnode-14', ' ')
#  nodes = string.split('node-20 node-21 node-23 node-24 node-25', ' ')
 # nodes = string.split('node-5', ' ')
  bfnode = 'node-1'

elif product == 'cgeadk':
  hosts = {
      'solaris7':  (['solaris8-4',], 'buildsparc', '/opt/dailybuild'),
          }
  nodes = string.split('node-1 node-2 node-4 node-5 oldnode-13 oldnode-14', ' ')
#  nodes = string.split('node-20 node-21 node-23 node-24 node-25', ' ')
 # nodes = string.split('node-5', ' ')
  bfnode = 'node-1'
elif product == 'ceeadk':
  hosts = {
      'windows2000':  (['cygwin-7',], 'buildcygwin','/home/build/dailybuild'),
          }
  nodes = string.split('node-4', ' ')
  bfnode = 'node-1'

elif product == 'cee':
  hosts = {
      'windows2000':  (['cygwin-7','cygwin-8'], 'buildcygwin','/home/build/dailybuild'),
          }
  nodes = string.split('node-8 node-9 node-10 node-11 node-12', ' ')
  bfnode = 'node-8'

elif product == 'mobilinux':
  hosts = {
      'windows2000':  (['cygwin-7','cygwin-8'], 'buildcygwin','/home/build/dailybuild'),
          }
  nodes = string.split('node-7 node-8 node-9 node-10 node-11', ' ')
  bfnode = 'node-8'

elif product == 'bst':
  hosts = { }
  nodes = string.split('node-1 node-2 node-3 node-4 node-5', ' ')
#  nodes = string.split('node-20 node-21', ' ')
#  nodes = string.split('node-20 node-21 node-22 node-23 node-24 node-25', ' ')

elif product == 'krapalua':
  hosts = {
#      'windows2000':  (['cygwin-7',], 'buildcygwin','/home/build/dailybuild'),
          }
  nodes = string.split('oldnode-14', ' ')
  #nodes = string.split('oldnode-14', ' ')
  bfnode = 'node-16'

elif product == 'krapthumb':
  hosts = {
      'windows2000':  (['cygwin-4',], 'buildcygwin','/home/build/dailybuild'),
          }
  nodes = string.split('node-16', ' ')

else:
  print "Unknown product: " + product
