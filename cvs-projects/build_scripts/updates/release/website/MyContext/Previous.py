from Queue import Queue

ErrType = type("")

class Previous(Queue):
	def title(self):
		return "Previous Cycles"


	def writeQueue(self):
		result = self.db.Command('''SELECT id FROM ReleaseAutomation.release_cycle WHERE processed="Y" ORDER BY process_date''')
		if type(result) == ErrType:
			self.writeError(result)
			return

		result = list(result)
		result.reverse()
		for cycle in result:
			id = int(cycle['id'])
			self.writeCycle(id)

		return


#end Previous
