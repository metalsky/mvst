#!/usr/bin/python
import os, string, sys

def parse_log(rpm_list,file,tarj):
  reject = '' 
  if os.path.exists(file):
    f_log = open(file,'r')
    while 1:
      line = f_log.readline()
      if line:
        if string.find(line,'finished buildtargetapps-1-' + tarj + '-script-setup') > -1:
          print "starting " + log + " parsing"
        elif string.find(line,'building buildtargetapps-2-' + tarj + '-script-setup') > -1:
          print "finished " + log + " parsing"
          f_log.close()
          break
        elif string.find(line,"Wrote") > -1 and string.find(line,'.mvl') > -1:
          #print string.strip(line)
          full_rpm_name = string.split(string.strip(line),'/')[5]
          rpm_list.append(string.split(full_rpm_name,tarj)[0])
        else:
          continue
      else:
        print "ERROR: empty file, skipping " + tarj + " log analysis..."
        reject = tarj
        break
  else:
    print "ERROR: " + file + " does not exist...skipping"
    reject = tarj
  return reject

if len(sys.argv) != 2:
  print 'usage: %s %s' % (sys.argv[0],'<buildtag>')
  print 'where <buildtag> is a foundation 3 (fthree) build.'
  print 'The ADK will be built from Pro, but the library/dev apps are all present in the'
  print 'foundation build (a couple are rebuilt in the Pro build).'
  sys.exit(1)

buildtag = sys.argv[1]
buildid = string.split(buildtag,'_')[1]

adk_uclibc_targets	= ('arm_v5t_le', 'arm_xscale_be', 'mips2_fp_be', 'x86_586',)
#adk_uclibc_targets	= ('arm_v5t_le', )
adk_targets		= ('mips64_fp_be', 'ppc_74xx', 'ppc_85xx', 'x86_pentium3', 'x86_pentium4')

logdir = '/mvista/dev_area/foundation/%s/logs' % buildtag

# generate a dictionary of built rpms
rpm_dict = {}
rpm_dict['common'] = []
rejects = []
for tarj in adk_uclibc_targets:
  rpm_dict[tarj] = []
  log = logdir + '/apps-' + tarj + '-' + buildid + '.log'
  reject = parse_log(rpm_dict[tarj],log,tarj)
  if reject:
    rejects.append(reject)
  rpm_dict[tarj + '_uclibc'] = []
  log = logdir + '/apps-' + tarj + '_uclibc-' + buildid + '.log'
  reject = parse_log(rpm_dict[tarj + '_uclibc'],log,tarj + '_uclibc')
  if reject:
    rejects.append(reject)
for tarj in adk_targets:
  rpm_dict[tarj] = []
  log = logdir + '/apps-' + tarj + '-' + buildid + '.log'
  reject = parse_log(rpm_dict[tarj],log,tarj)
  if reject:
    rejects.append(reject)

print 'number of rejects = ' + str(len(rejects))
print 'rejected targets = '
print rejects
#print "dict:"
#print rpm_dict

all_targets = rpm_dict.keys()
all_targets.remove('common')
print 'total number of targets = ' + str(len(all_targets)) 
if rejects:
  for reject in rejects:
    all_targets.remove(reject)
common_val = len(all_targets)
print 'number need for a common app = ' + str(common_val)

for tarj in all_targets:
  print 'tarj = ' + tarj
  temp_apps = []
  for app in rpm_dict[tarj]:
    temp_apps.append(app)
  #print 'temp_apps = '
  #print temp_apps
  for app in temp_apps:
    print 'app = ' + app
    count = 0
    for target in all_targets:
      #print 'checking if %s is in rpm_dict[%s]..' % (app,target)
      if app in rpm_dict[target]:
        count += 1
    print 'found %s matches...need %s to be common' % (str(count),str(common_val)) 
    if count == common_val:
      print 'moving %s to common and removing from all_targets' % app
      rpm_dict['common'].append(app)
      for target in all_targets:
        rpm_dict[target].remove(app)

#print "dict: "
#for key in rpm_dict.keys():
#  print key + ':'
#  print rpm_dict[key]
#  print ' '

os.system('mkdir -p %s/../adkfiles' % logdir)
for key in rpm_dict.keys():
  f_list = open('%s/../adkfiles/apps-%s-%s' % (logdir,key,buildid),'w')
  for app in rpm_dict[key]:
    f_list.write(app + key + '.mvl\n')
  f_list.close()
