
class Frame(object):

	def __init__(self, frameNum=None, img=None, boxes=None):
		self.frameNum = frameNum
		self.img = img
		self.boxes = boxes

		self.fillBoxes()


		# boxes = [ (id, box), ...]
		# box = {x1, y1, x2, y2, col}

	def fillBoxes(self):
		# parse data
		self.boxes = []


	def addBox(self, box, id=None):
		# add new tuple with box and identity
		# box = {x1, y1, x2, y2}
		pass

	def commitBoxes():
		# write new boxes into file
		pass