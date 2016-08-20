class BiosUpdater():
	
	def __init__(self, params, target_path):
		raise NotImplementedError()

	def update(self, data):
		raise NotImplementedError()
	
	def fail(msg):
		print("Error: %s" % msg)
		sys.exit(1)