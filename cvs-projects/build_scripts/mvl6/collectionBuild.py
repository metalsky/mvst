#!/usr/bin/env python
import sys, server, os, commands, re
from datetime import datetime
from filecmp import dircmp
NAME,VER = 0,1

class collectionBuild:
	def __init__(self):
		try:
			self.BuildTag = sys.argv[1]
		except:
			raise SyntaxError, "Arguments not specified.  Aborting."
		self.BuildID = self.BuildTag.split('_')[2]
		self.RepoNames = self.fetchRepoNames()
		self.VersionString = datetime.now().strftime("%y%m%d%H%M")
		if self.RepoNames == None:
			raise SyntaxError, "Something is wrong with the SQL command.  Aborting."

		

	def fetchRepoNames(self):
		retList = []
		db = server.server()
		db.Connect()
		results = db.Command("SELECT DISTINCT name FROM Mvl6Cfg.Repos")
		db.Close()
		for result in results:
			retList.append(result['name'])
		return retList

	def fetchMSDNames(self):
		retList = []
		db = server.server()
		db.Connect()
		results = db.Command("SELECT name, kernelVer FROM Mvl6Cfg.MSDs")
		db.Close()
		for result in results:
			retList.append((result['name'],  result['kernelVer']))
		return retList

	def createKernelOutput(self):
		changedKernels = []
		os.chdir('/mvista/dev_area/mvl6/mvlinux')
		os.system('/home/build/ip/montavista/bin/git fetch')

		for msd in self.fetchMSDNames():
			msdTag = msd[NAME] + '-' + msd[VER]

			os.makedirs('/mvista/dev_area/mvl6/%s/%s' % (self.BuildTag, msd[NAME]))
			os.system('/home/build/%s-exp/CVSREPOS/build_scripts/mvl6/ol-git-mvl6-releasify -r /mvista/dev_area/mvl6/mvlinux origin/mvl-%s/msd.%s /mvista/dev_area/mvl6/%s/%s' \
						% (self.BuildTag, msd[VER], msd[NAME], self.BuildTag, msd[NAME]))

			#os.system('git tag -a -m "%s" %s_cbuild_%s  origin/mvl-%s/msd.%s' % (msdTag, msdTag, self.BuildID, msd[VER], msd[NAME]))


			#Get logs
			tags = commands.getoutput('git tag -l | grep cbuild | grep %s | tail -n2' % msd[NAME])

			compObj = commands.getoutput('diff -urp /mvista/dev_area/mvl6/latest_collection/%s /mvista/dev_area/mvl6/%s/%s' % (msd[NAME], self.BuildTag, msd[NAME]))

			if compObj == '':
				fileDiff = False
			else:
				fileDiff = True

			originDirExists = os.path.exists('/mvista/dev_area/mvl6/latest_collection/%s' % msd[NAME])

			if not fileDiff and originDirExists:
				os.system('cp /mvista/dev_area/mvl6/latest_collection/%s-* /mvista/dev_area/mvl6/%s' % (msd[NAME], self.BuildTag))
			#There is either a difference or its brand new.
			else:
				os.system('pushd /mvista/dev_area/mvl6/%s > /dev/null;tar jcvf %s-%s.tar.bz2 %s > /dev/null;echo "%s-%s.tar.bz2" > %s-fname;popd > /dev/null' \
						% (self.BuildTag, msdTag, self.VersionString, msd[NAME], msdTag, self.VersionString, msd[NAME]))
				os.system('git tag -a -m "%s" %s-%s  origin/mvl-%s/msd.%s' % (msdTag, msdTag, self.VersionString, msd[VER], msd[NAME]))
				changedKernels.append(msdTag)
			

		os.system('git push --tags')
		os.chdir('/mvista/dev_area/mvl6/%s' % self.BuildTag)
		fp = open('changed_kernels', 'w')
		for kernel in changedKernels:
			fp.write('%s\n' % kernel)
		fp.close()
	
	
	
	def TagRepos(self):
		os.chdir('/mvista/dev_area/mvl6/%s' % self.BuildTag)
		for repo in self.ChangedRepos:
			fp = open('%s-ver' % repo)
			version = fp.readline().strip()
			print '%s-%s' % (repo,version)
			commands.getoutput('''pushd ./%s;git tag -a -m "%s-%s" %s-%s;git push --tags;popd'''% (repo, repo, version, repo, version))
			fp.close()


	def TagSources(self):
		cwd = os.getcwd()
		build_dir = os.path.join('/mvista/dev_area/mvl6/', self.BuildTag)
		os.chdir(build_dir)
		for repo in self.ChangedRepos:
			fp = open('%s-ver' % repo)
			version = fp.readline().strip()
			fp.close()
			os.system('git clone git.sh.mvista.com:/var/cache/git/mvl6/%s-sources.git' % repo)
			os.system('pushd %s-sources > /dev/null; git tag %s-%s; git push --tags; popd > /dev/null' % (repo, repo, version))
		os.chdir(cwd)

			
			
	def createOutput(self):
		reposToBuild = []
		destDir = '/mvista/dev_area/mvl6/%s' % self.BuildTag
		os.mkdir(destDir)
		os.chdir(destDir)
		for repo in self.RepoNames:
			if os.path.exists('/mvista/dev_area/mvl6/latest_collection/%s' % repo):
				os.system('cp /mvista/dev_area/mvl6/latest_collection/%s . -R' % repo)
				output = commands.getoutput('''pushd ./%s > /dev/null;git pull;popd > /dev/null''' % repo).split('\n')
				upToDate =  'Already up-to-date.' in output
				print output
				print upToDate
				commands.getoutput('''pushd ./%s;git tag cbuild_%s;git push --tags;popd'''% (repo, self.BuildID))
				if not upToDate:
					reposToBuild.append(repo)
					os.system('tar jcvf %s-%s.tar.bz2 %s --exclude "%s/.git" --exclude "%s/.gitignore"' % (repo, self.VersionString, repo, repo, repo))
					os.system('echo %s > %s-ver' % (self.VersionString, repo))
				else:
					os.system('cp /mvista/dev_area/mvl6/latest_collection/%s-* .' % repo)
			else:
				os.system('git clone git.sh.mvista.com:/var/cache/git/mvl6/%s.git' % repo)
				commands.getoutput('''pushd ./%s;git tag cbuild_%s;git push --tags;popd'''% (repo, self.BuildID))
				reposToBuild.append(repo)
				os.system('tar jcvf %s-%s.tar.bz2 %s --exclude "%s/.git" --exclude %s/.gitignore' % (repo, self.VersionString, repo, repo, repo))
				os.system('echo %s > %s-ver' % (self.VersionString, repo))



		fp = open('changed_repos', 'w')
		for repo in reposToBuild:
			fp.write(repo)
			fp.write('\n')
		fp.close()
		self.ChangedRepos = reposToBuild

	def UpdateLink(self):
		os.chdir('/mvista/dev_area/mvl6')
		os.system('rm -f latest_collection')
		os.system('ln -s %s latest_collection' % self.BuildTag)

def genCommitList():
	commits = []
	re_author = re.compile(r'Author: (.*) <(.*)>')
	re_commit = re.compile(r'commit (.*)')
	re_date   = re.compile(r'Date: (.*)')

	latestCollectionDir = '/mvista/dev_area/mvl6/latest_collection'
	for file in os.listdir(latestCollectionDir):
		currentDir = os.path.join(latestCollectionDir, file)
		if not os.path.isdir(currentDir):
			continue
		os.chdir(currentDir)
		tags = commands.getoutput('git tag -l | grep cbuild| tail -n2').split('\n')
		print file
		print tags
		#The non-git repos, and the <tag>-sources repos won't have tags, so skip.
		if tags == ['fatal: Not a git repository'] or tags == [''] or len(tags) == 1:
			continue
		#print commands.getoutput('git log %s..%s' % (tags[0], tags[1]))
		log = commands.getoutput('git log %s..%s' % (tags[0], tags[1])).split('\n')
		print log


		commitID = authorName = emailAddress = commitDate = None
		bodyStr = ''
		for line in log:
			#Commit
			matchObj = re_commit.match(line)
			if matchObj:
				#If we are back here, we are at a new file or a new commit.  Need to instantiate and reset if it's not the first.
				try:
					if commitID and authorName and emailAddress and commitDate:
						com = GitCommit(file, commitID, authorName, emailAddress, commitDate, bodyStr)
						commits.append(com)
						commitID = authorName = emailAddress = commitDate = None
						bodyStr = ''

				#we are at the start
				except UnboundLocalError:
					pass

				commitID = matchObj.group(1)
				continue

			#Author
			matchObj = re_author.match(line)
			if matchObj:
				authorName, emailAddress = matchObj.group(1), matchObj.group(2)
				continue

			#Date
			matchObj = re_date.match(line)
			if matchObj:
				commitDate = matchObj.group(1).strip()
				continue

			bodyStr += line + '\n'

		#Gotta repeat this after the log is over to grab the last one
		if commitID and authorName and emailAddress and commitDate:
			com = GitCommit(file, commitID, authorName, emailAddress, commitDate, bodyStr)
			commits.append(com)
			commitID = authorName = emailAddress = commitDate = None
			bodyStr = ''




	return commits





class GitCommit:
	def __init__(self, repo, id, name, email, date, body):
		self.Repo = repo
		self.CommitID = id
		self.AuthorName = name
		self.AuthorEmail = email
		self.CommitDate = date
		self.CommitBody = body

	def dbgout(self):
		print '*****\n'
		print 'repo %s' % self.Repo
		print 'commit %s' % self.CommitID
		print 'name %s' % self.AuthorName
		print 'email %s' % self.AuthorEmail
		print 'commitdate %s' % self.CommitDate
		print 'body:'
		print self.CommitBody



		

if __name__ in ['__main__']:
	mycb = collectionBuild()
	mycb.createOutput()
	mycb.createKernelOutput()
	mycb.UpdateLink()
	mycb.TagRepos()
	mycb.TagSources()
	
