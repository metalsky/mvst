from Queue import Queue

ErrType = type("")


class Current(Queue):
	def title(self):
		return "Current Cycle"

	
	
	def writeQueue(self):
		#Last updated:
		updated = []
	
		result = self.db.Command('''SELECT MAX(ts) FROM ReleaseAutomation.mod_info''')
		if type(result) == ErrType:
			self.writeError(result)
			return
		stats = result[0]
		last_updated = str(stats['MAX(ts)'])
		line_style = '''size="1" noshade width="90%"'''
		self.writeln('''<center><b>Last Updated: %s</b></center><br><hr %s><p>'''%(last_updated, line_style))

		
		
		#ASYNCS first
		result = self.db.Command('''SELECT id FROM ReleaseAutomation.release_cycle WHERE async="Y" AND processed="N" ORDER BY process_date''')
		if type(result) == ErrType:
			self.writeError(result)
			return 
		
		#build unique cycle list
		cycle_list = []
		for request in result:
			id = int(request['id'])
			if id not in cycle_list:
				cycle_list.append(id)
		#end for
		
		#display asyncs
		if cycle_list:
			self.writeln('''<b>ASYNC Requests:</b><br><p>''')
			cycle_list.reverse()
			for cycle in cycle_list:
				self.writeCycle(cycle)
			#end for
			self.writeln('''<br><p>''')
		#else

		#Normal release cycles
		result = self.db.Command('''SELECT id from ReleaseAutomation.release_cycle WHERE processed="N" AND async="N"''')
		if type(result) == ErrType:
			self.writeError(result)
			return

		#build release only list
		regular_list = []
		for cycle in result:
			id = int(cycle['id'])
			if id not in cycle_list and id not in regular_list:
				regular_list.append(id)
		#end for

		#display regular cycles
		if regular_list:
			self.writeln("<b>Current Updates in the Queue:</b><br><p>")
			regular_list.sort()
			for cycle in regular_list:
				self.writeCycle(cycle)
			#end for
		#else	

		return

#end Previous
