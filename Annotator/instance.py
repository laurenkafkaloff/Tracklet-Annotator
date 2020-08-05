
class Instance(object):

	def __init__(self, id=None, color=None):
		self.id = id
		self.color = color
		self.boxes = {} # { framenum: box }
		self.maxFrame = 0
		# box = {x1, y1, x2, y2}


	def updateBoxes(self, box, frameNum):
		# don't forget to add instance to frame obj if new box
		self.boxes[frameNum] = self.cleanBox(box)
		if frameNum > self.maxFrame:
			self.maxFrame = frameNum

	def updateId(self, newId, frameNum, oldFrames):
		newFrames = oldFrames
		for key in self.boxes:
			if int(key) >= frameNum:
				workingFrame = oldFrames[int(key)] # frame
				workingFrame.instances[prevId] = self.boxes[key]
				workingFrame.instances.pop(self.id)
				newFrames[int(key)] = workingFrame
		return newFrames


	def swapId(self, bird2, frameNum, oldFrames):
		# frame will store all instances on it in a dictionary { instance: box }
		newFrames = oldFrames
		a, b = {}, {}, {}, {}
		for key in self.boxes:
			if int(key) < frameNum:
				a[key] = self.boxes[key]
			else:
				b[key] = self.boxes[key]
				if self.maxFrame >= bird2.maxFrame:
					workingFrame = oldFrames[int(key)] # frame
					bbox = workingFrame.instances.get(bird2.id) # box for an instance
					workingFrame.instances[bird2.id] = self.boxes[key]
					if not bbox is None: # this frame, in addition to a, showed b
						workingFrame.instances[self.id] = bird2.boxes[key]
					newFrames[int(key)] = workingFrame
		for key in bird2.boxes:
			if int(key) < frameNum:
				b[key] = bird2.boxes[key]
			else:
				a[key] = bird2.boxes[key]
				if bird2.maxFrame > self.maxFrame and key <= self.maxFrame:
					workingFrame = oldFrames[int(key)]
					abox = workingFrame.instances.get(self.id)
					workingFrame.instances[self.id] = bird2.boxes[key]
					if not abox is None: # this frame, in addition to b, showed a
						workingFrame.instances[bird2.id] = self.boxes[key]
					newFrames[int(key)] = workingFrame
		self.boxes = a
		bird2.boxes = b

		return newFrames # be updated with correctly swapped rectangles


	def cleanBox(self, box):
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

		return {"x1":newx1, "y1":newy1, "x2":newx2, "y2":newy2}
