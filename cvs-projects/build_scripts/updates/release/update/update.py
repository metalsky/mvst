import aspects

import db
import generic

import mvlapt as apt
import mvl


def dispatchWrapper(self, *args, **keyw):
	'''
	This wraps around the generic update class methods and intercepts 
	the calls routing them to the apt or mvl version.
	'''
	stack_entry = self.__proceed_stack[-1]

	#remove class from method name
	s = stack_entry.name.split('.')
	if len(s) > 1:
		name = s[-1]
	else:
		name = s[0]
	
	#look for method in new class
	if name in dir(self._run_class):
		real = getattr(self._run_class, name)
		if callable(real):
			return real(*args, **keyw)
	#else:
	return self.__proceed(*args, **keyw)
#end dispatchWrapper


class update(generic.update):
	'''
	This update class should be exported byt he pyro server.It will 
	handle calling the appropriate apt or mvl methods, and also ensure
	that anything that is unimplemented is handled properly.
	'''
	def __init__(self, *args, **keyw):
		generic.update.__init__(self, *args, **keyw)
		
		#Choose which update class to run based on ProductID
		d = db.db()
		d.Connect()
		ret = d.Command('''SELECT * FROM BuildCfg.products WHERE id=%d'''%(int(self.ProductID)))
		d.Close()
		p = ret[0]

		if p['version'] >= "5.0":
			self._run_class = apt.update(self.ProductID)
		else:
			self._run_class = mvl.update(self.ProductID)
		#wrap only the export methods by generic
		for member in dir(self):
			if str(member)[0].isalpha():
				real = getattr(self, member)
				if callable(real):
					aspects.wrap_around(real, dispatchWrapper)
		return
				

