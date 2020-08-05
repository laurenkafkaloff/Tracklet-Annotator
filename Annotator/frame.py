
class Frame(object):

	def __init__(self, frameNum=None, img=None):
		self.frameNum = frameNum
		self.img = img
		self.instances = []

		# self.fillBoxes()


		# box = {x1, y1, x2, y2}

	def fillBoxes(self):
		file = open("/Users/laurenkafkaloff/Desktop/TestData.txt","r")
		print(file.readline())
		# parse data
		# let boxes index = identity number
		# RESIZE BOXES BASED ON IMAGE SIZE
		self.boxes = {}


	def addInstance(self, id):
		self.instances.append(id)

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
