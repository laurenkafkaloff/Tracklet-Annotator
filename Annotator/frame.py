
class Frame(object):

	def __init__(self, frameNum=None, img=None):
		self.frameNum = frameNum
		self.img = img
		self.instances = {} # { id : box }

		# box = { x1, y1, x2, y2, color }
	def addInstance(self, id, box):
		self.instances[id] = box

	def removeInstance(self, id):
		self.instances.pop(id)
