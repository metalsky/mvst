import os, shutil
def safecopy(source, dest): #{{{
	''' Checks to see if the destination file exists before copying.
	 	If it does, the copy is skipped.'''

	if os.path.isfile(source):
		fileName = os.path.split(source)[1]
		if os.path.exists( os.path.join(dest,fileName) ):
			return
		else:
			try:
				shutil.copy(source,dest)
			except IOError:
				pass
				#print "%s to %s copy failed." % (source, dest)
	else:
		try:
			if os.path.exists(source) and not os.path.exists(dest):
				#This nonsense is fixed in python 2.5, if we ever upgrade, remove these 2 lines.
				os.makedirs(dest)
				shutil.rmtree(dest)

				shutil.copytree(source,dest)

		except IOError:
			pass
			#print "%s to %s copy failed." % (source, dest)
#}}}
