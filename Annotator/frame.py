
class Frame(object):

	def __init__(self, frameNum=None, img=None):
		self.frameNum = frameNum
		self.img = img
		self.instances = {}
		# { id: box }

		# self.fillBoxes()


		# box = {x1, y1, x2, y2}

	def fillBoxes(self):
		file = open("/Users/laurenkafkaloff/Desktop/TestData.txt","r") 
		print(file.readline())
		# parse data
		# let boxes index = identity number
		# RESIZE BOXES BASED ON IMAGE SIZE
		self.boxes = {}


	def addInstance(self, id, box):
		# box = {x1, y1, x2, y2}
		# make the box go from top left to bottom right
		if box['x1'] > box['x2']:
			newx1, newx2 = box['x2'], box['x1']
		else: 
			newx1, newx2 = box['x1'], box['x2']
		if box['y1'] > box['y2']:
			newy1, newy2 = box['y2'], box['y1']
		else: 
			newy1, newy2 = box['y1'], box['y2']

		self.instances[id] = {"x1":newx1, "y1":newy1, "x2":newx2, "y2":newy2}

	def swapBoxes(self, box1, box2):
		# add new tuple with box and identity
		# box = {x1, y1, x2, y2, id}
		pass

	def updateID(self, box, id):
		# include IDs from previous frame
		pass

	def commitBoxes():
		# write new boxes into file
		pass




	# frame will store all instances on it in a dictionary { instance: box }
	# 