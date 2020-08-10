from Annotator.frame import Frame
import copy

class Instance(object):

	def __init__(self, id=None, index=None, color="white", colorName="white"):
		self.id = id
		self.color = color
		self.colorName = colorName
		self.index = index
		self.boxes = {} # { framenum: box }
		self.maxFrame = 0

	def updateBoxes(self, box, frame):
		self.boxes[frame.frameNum] = self.cleanBox(box)
		if frame.frameNum > self.maxFrame:
			self.maxFrame = frame.frameNum
		frame.addInstance(self.id, box)

	def updateId(self, newId, frameNum, oldFrames): # for changing id that's not on frame -- think you can just run swapid?
		newFrames = oldFrames
		for key in self.boxes:
			if int(key) >= frameNum:
				workingFrame = oldFrames[int(key)] # frame
				workingFrame.instances[newId] = self.boxes[key]
				workingFrame.instances.pop(self.id)
				newFrames[int(key)] = workingFrame
		return newFrames

	def swapId(self, second, frameNum, frames, idsHaveChanged):
		# frame will store all instances on it in a dictionary { instance: box }
		a = self
		b = second
		laterTrack = b
		if a.maxFrame >= b.maxFrame:
			laterTrack = a

		idsHaveChanged.append(a)
		idsHaveChanged.append(b)

		keys = copy.deepcopy(list(laterTrack.boxes.keys()))
		for key in keys:
			key = int(key)
			if key >= frameNum:
				a_short = a.boxes.get(key)
				b_short = b.boxes.get(key)
				a_long = frames[key].instances.get(a.id)
				b_long = frames[key].instances.get(b.id)

				aIsNone, bIsNone = True, True
				if a_short is not None:
					a_short['color'] = str(b.color)
					a_long['color'] = str(b.color)
					aIsNone = False
				if b_short is not None:
					b_short['color'] = str(a.color)
					b_long['color'] = str(a.color)
					bIsNone = False

				a.boxes[key], b.boxes[key] = b_short, a_short
				frames[key].instances[a.id], frames[key].instances[b.id] = b_long, a_long

				if aIsNone:
					b.boxes.pop(key)
					frames[key].instances.pop(b.id)
					a_short = False
				if bIsNone:
					a.boxes.pop(key)
					frames[key].instances.pop(a.id)
					b_short = False

		a.maxFrame, b.maxFrame = b.maxFrame, a.maxFrame

	def cleanBox(self, box):
		# box = { x1, y1, x2, y2, color }
		# make the box go from top left to bottom right
		if box['x1'] > box['x2']:
			newx1, newx2 = box['x2'], box['x1']
		else:
			newx1, newx2 = box['x1'], box['x2']
		if box['y1'] > box['y2']:
			newy1, newy2 = box['y2'], box['y1']
		else:
			newy1, newy2 = box['y1'], box['y2']

		return {"x1":newx1, "y1":newy1, "x2":newx2, "y2":newy2, "color":self.color}
