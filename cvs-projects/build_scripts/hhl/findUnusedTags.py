#!/usr/bin/env python

buildsTemp = open('updatesFromBuilds.txt').readlines()
taglistTemp = open('taglist').readlines()


buildsOnZone = []
for buildID in buildsTemp:
	buildsOnZone.append(buildID.strip('\n'))


CVSTags = []
for tag in taglistTemp:
	CVSTags.append(tag.strip('\n'))



tagsToDelete = []

for tag in CVSTags:
	if tag[-7:] not in buildsOnZone:
		tagsToDelete.append(tag)

tagsToDelete.sort()

for tag in tagsToDelete:
	print tag
