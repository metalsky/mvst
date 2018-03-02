#!/usr/bin/env python
import os, re, sys, DBInteraction


dirs = []
msds = {}
keepers = []
msds_remove = []


def get_retention():
	# let's get the builds in retention into a list:
	retentiondb = DBInteraction
	for n in retentiondb.fetchKeepers():
		keepers.append(n[1])


def get_dirs():
	# generate a list of builds to reconcile against the "keepers" list:
	os.chdir("/mvista/dev_area/mvl6")
	for x in os.listdir("."):
		if os.path.isdir(x) and not os.path.islink(x):
			dirs.append(x)

	# now find all directories that match our regex and create an index keyed from msd name:
	msd_regex = re.compile(r'(.*)_(.*)_(.*)')

	for dir in dirs:
		msd_match = msd_regex.match(dir)
		if msd_match:
			if msd_match.group(1) not in msds.keys() and msd_match.group(1) != 'collection':
				msds[msd_match.group(1)] = []
			if msd_match.group(1) in msds.keys():
				msds[msd_match.group(1)].append(dir)


def prune_dirs():
	# find candidates for removal:
	five = 5
	candidate = msds.keys()
	candidate.sort()
	for n in candidate:
		retention = 0
		msds[n].sort()
		for msd in msds[n]:
			if msd in keepers:
				# just debugging
				# print "\t%s in keepers" % msd
				retention += 1
				msds[n].remove(msd)

		""" Used for original debugging, uncomment if you want debugging:
		print "%s: " %(n)
		print "\t%d in retention" %(retention)
		print "\t%d MSD build directories" %(len(msds[n]))
		print "\t%s" %(msds[n])
		print "\tWe will be keeping the following builds: %s" %(msds[n][-(five - retention):])
		"""

		for monkey in msds[n]:
			if monkey not in (msds[n][-(five - retention):]):
				# again, more debugging
				# print "\tDeleting: %s" % monkey
				msds_remove.append(monkey)

	# even more debugging
	# print msds_remove
	for x in msds_remove:
		print "Deleting %s" %(x),
		sys.stdout.flush()
		os.system("/bin/rm -rf %s" %(x))
		print "done."
	
	print
	print


get_retention()
get_dirs()
prune_dirs()
