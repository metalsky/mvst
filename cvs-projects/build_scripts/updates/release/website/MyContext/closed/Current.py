from navigation import SitePage


class Current(SitePage):

	def awake(self, trans):
		SitePage.awake(self, trans)
		session = trans.session()
		request = trans.request()
		app = trans.application()
		
		session.values().clear()
		request.setURLPath("/")
		app.forward(trans, 'Main')
	
		return
