#!/usr/bin/env python
import re,os,sys,DBInteraction

class keepers:
	def __init__(self,buildtag):
		self.numTagsToKeep = 5
		self.tagList = []
		# get retention list
		self.dbi = DBInteraction
		self.dbi.testDB()
		self.dbi.removeAllBugz()
		self.dbi.addBugzToDB()
		self.dbi.repopulateDB()
		exemptions = self.dbi.fetchKeepers()
		tagPrefix = buildtag.split('_')[0]
		# look for all similar tags in the exemptions
		for line in exemptions:
			if tagPrefix in line[1]:
				self.tagList.append(line)

	def updateTags(self,buildtag):
		purge = 0
		numToPurge = 0
		tagPrefix = buildtag.split('_')[0]
		if len(self.tagList) >= self.numTagsToKeep:
			print "There are %s matching tags in the exemptions, only %s will be kept" % (str(len(self.tagList)),str(self.numTagsToKeep))
			purge = 1
		# add exemption
		self.tagList.append(['000',buildtag])
		self.dbi.addKeeper(buildtag, 'MANUAL')
		# remove any extra tags
		self.tagList.sort()
		if purge:
			numToPurge = len(self.taglist) - self.numTagsToKeep
			count = 0
			while count < numToPurge:
				print "Removing exemption for: %s" % self.taglist[count][1]
				self.dbi.removeKeeper(self.taglist[count][0])
				count += 1

if __name__ in ['__main__']:
  if len(sys.argv) != 2:
    print 'usage: %s %s' % (sys.argv[0],'<buildtag>')
    sys.exit(0)
  buildtag = sys.argv[1]
  mvl6keepers = keepers(buildtag)
  mvl6keepers.updateTags(buildtag)
