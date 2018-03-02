
import os, sys, string
def getmsd(dir):
	if os.path.exists("%s/content/prebuilt" % dir):
		tmp = os.listdir("%s/content/prebuilt" % dir)
	else:
		return ""
	if len(tmp) == 1:
		return (tmp[0])
	else:
		return ""


def generate(dirList, outFile):	
	targetUrl="http://collective.sh.mvista.com/dev_area/mvl6/"
	
	header='<?xml version="1.0" encoding="ISO-8859-1"?>\n' \
	'<content server-time="2009-05-08T20:25:50.0Z">\n' \
	'<result>success</result>\n' \
	'<token>pL5PSuqoZ9YmaNOFJkgqybj1TrviKEAmVONWbmzX8cs=</token>\n' \
	'<msds>\n'
	
	msditem='	<msd id="%s" description="%s prebuilt binaries">\n' \
	'		<subscription start-time="2009-05-08T20:25:50.0Z" end-time="2199-07-09T04:25:50.0Z"/>\n' \
	'		<url-info start-time="2009-05-08T20:25:50.0Z" url="%s" end-time="2199-07-09T04:25:50.0Z"/>\n' \
	'	</msd>\n' 
	
	collectionstart='</msds>\n<collections>\n'
	
	collectionitem='	<collection type="%s" ordering="%s" id="%s" description="%s collection for %s">\n' \
	'		<subscription start-time="2009-05-08T20:25:50.0Z" end-time="2199-07-09T04:25:50.0Z"/>\n' \
	'		<url-info start-time="2009-05-08T20:25:50.0Z" url="%s" end-time="2199-07-09T04:25:50.0Z"/>\n'\
	'%s\n'\
	'	</collection>\n'
	msdgrouptag='		<msd-group id="%s"/>\n'
	footer='</collections></content>'
	#msdurl="%s%s/content/prebuilt/%s/"
	msdurl="%s%s/content/msds/%s/"
	collectionurl="%s%s/content/collections/%s/"
	fileset = set(['all', 'latest'])
	omitset = set(['toolchain'])
	collectionset = set(['foundation', 'core'])
	msdblacklistset = collectionset | fileset | omitset
	msditems=""
	collectionitems=""
	generalgroup=""
	msds= {}
	collections = []
	for each in dirList: 
		msd =""
		collectionset = set(['foundation', 'core'])
		msddir = os.path.basename(each)
		if not msddir:
			msddir = os.path.dirname(each)
			msddir = os.path.basename(msddir)
		blah = os.listdir("%s/content/collections" % each)
		msd = getmsd(each)
		if msd == "":
			continue	
		for collection in set(blah) - fileset - collectionset:
			if os.path.exists("%s/content/collections/%s/sources/" % (each, collection)):
				releases = os.listdir("%s/content/collections/%s/sources/" % (each, collection))
				for release in releases:
					if release.find("linux-") != -1:
						msd = collection
						break
				if msd != collection:
					collections += [ collection ]
		collectionset = set (collections) | collectionset
		msdurlitem= msdurl % (targetUrl, msddir, msd)
		msditems += msditem % (msd, msd, msdurlitem)
		generalgroup += msdgrouptag % (msd)
		msds[msd]=msddir
	
	order=1
	for msd in msds.keys():
		collectionurlitem = collectionurl % (targetUrl,msds[msd], msd)
		groupitem = msdgrouptag % msd
		collectionitems += collectionitem % ("kernel", order, msd, "kernel", msd, collectionurlitem, groupitem)
	
	for collection in collectionset:
		order += 1
		collectionurlitem = collectionurl % (targetUrl, msddir, collection)
		collectionitems += collectionitem % ( \
			collection, order, collection, collection, msd, collectionurlitem, generalgroup)
	fp = open(outFile, 'w')
	fp.write(header)
	fp.write(msditems)
	fp.write(collectionstart)
	fp.write(collectionitems)
	fp.write(footer)
	fp.close()
