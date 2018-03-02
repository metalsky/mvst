from navigation import SitePage

ErrType = type("")

class BugInstructions(SitePage):
	def title(self):
		return "Bug Instructions"

	def writeContent(self):
		adapterName = self.request().adapterName()
		
		self.writeln('''There are a few important parts of a bug that the ReleaseAutomation system pulls information from when processing your request.<br>All these fields should be filled out as part of the bug fixing process. Please make sure the following fields are correct:''')
		self.writeln('''<p><b>Fixed In</b> - This tells the system where to pull your updates from. The listed builds also tell it which products it should upload the update to. <b>NOTE:</b> If you checked your fix into a foundation branch, the fixed in field should contain a foundation build.''')
		self.writeln('''<p><b>Customer Viewable Flag</b> - This needs to be checked. Its what makes the Customer Viewable Description available for customers to see.''')
		self.writeln('''<p><b>Customer Viewable Description</b> - This should contain the following parts: <b>Products, Problem Description, Root Cause, How Solved, and Impact</b>(optional).''')
		self.writeln('''<p><b>State</b> - Bugs need to be in either the <b>VERIFIED</b> or <b>CLOSED</b> state to be released. By marking a bug VERIFIED, you are acknowledging that you have tested your fix.''')

		self.writeln('''<p> See <a href="http://wiki.sh.mvista.com/thebazaar2/bin/view/Process/BugzEntry">Bugz Process Page</a> for more information on bug fields and processes.<br><p>''')
		self.writeln('''<img src="%s/bugExample.png" alt="bugExample">'''%adapterName)
		return

#end bugInstructions
