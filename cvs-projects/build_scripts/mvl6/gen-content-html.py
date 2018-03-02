#!/usr/bin/env python
import os, sys, string

targetUrl="http://collective.sh.mvista.com/dev_area/mvl6/"

header='<?xml version="1.0" encoding="ISO-8859-1"?>\n' \
'<content server-time="2009-05-08T20:25:50.0Z">\n' \
'<result>success</result>\n' \
'<token>pL5PSuqoZ9YmaNOFJkgqybj1TrviKEAmVONWbmzX8cs=</token>\n' \
'<msds>\n'

msditem='	<msd id="%s" description="%s prebuilt binaries">\n' \
'		<subscription start-time="2009-05-08T20:25:50.0Z" end-time="2009-07-09T04:25:50.0Z"/>\n' \
'		<url-info start-time="2009-05-08T20:25:50.0Z" url="%s" end-time="2009-07-09T04:25:50.0Z"/>\n' \
'	</msd>\n' 

collectionstart='</msds>\n<collections>\n'

collectionitem='	<collection type="%s" ordering="%s" id="%s" description="%s collection for %s">\n' \
'		<subscription start-time="2009-05-08T20:25:50.0Z" end-time="2009-07-09T04:25:50.0Z"/>\n' \
'		<url-info start-time="2009-05-08T20:25:50.0Z" url="%s" end-time="2009-07-09T04:25:50.0Z"/>\n'\
'%s\n'\
'	</collection>\n'
msdgrouptag='		<msd-group id="%s"/>\n'
footer='</collections></content>'
msdurl="%s%s/content/prebuilt/%s/"
collectionurl="%s%s/content/collections/%s/"
collectionset = set(['foundation', 'core'])
fileset = set(['all', 'latest'])
omitset = set(['toolchain'])
msdblacklistset = collectionset | fileset | omitset
msditems=""
collectionitems=""
generalgroup=""
msds= {}
for each in sys.argv[1:]: 
	msddir = os.path.basename(each)
	if not msddir:
		msddir = os.path.dirname(each)
		msddir = os.path.basename(msddir)
	blah = os.listdir("%s/content/collections" % each)	
	blahset = set(blah)
	msd = (blahset - msdblacklistset).pop()
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
print header
print msditems
print collectionstart
print collectionitems
print footer
