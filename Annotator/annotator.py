import tkinter as tk
from tkinter import *
from tkinter import filedialog, simpledialog
from PIL import ImageTk,Image
import time
import threading
import os
import math
import copy

from Annotator.frame import Frame
from Annotator.instance import Instance
from Annotator.colors import ColorSetter
import cv2

class Annotator():
	# TODO: Organize identities into on curr frame, prev frame, next frame when entering edtior mode
	# TODO: Add new writable file to folder with some consistent naming scheme, only store changes and don't commit them, have option to merge files
	# NOTE: Export environment into github
	# CASE: Opening a second video -- need to reset like everything

	def __init__(self):
	# Instance Variables
		# DISPLAY
		self.width, self.height = 960, 600 # width overwritten by screensize
		self.border = 10
		self.top_two_bars = 45
		self.leftPanelWidth = 200
		self.leftPanelHeight_Row0 = 200
		self.leftPanelHeight_Row1 = 10
		self.leftPanelHeight_Row2 = 50

		self.displayedIdent1Height = 15
		self.displayedIdent2Height = 15

		# FILLING VIDEO
		self.filling = False
		self.tempCount = 0
		self.fileProg = 0

		# PLAYING VIDEO
		self.textFileName = None
		self.videoFileName = None
		self.video = None
		self.stopEvent = threading.Event()
		self.playing = False
		self.frames = [Frame(frameNum=0)]
		self.curr = Frame(frameNum=0)
		self.displayedImage = None

		# BOUNDING BOXES
		self.drawing = False
		self.edited = False
		self.rect = None
		self.minBoxSize = 10
		self.curr_box = {"x1":0, "y1":0, "x2":0, "y2":0}
		self.curr_id = None
		self.saveBox = None
		self.topLevelOpen = False
		self.boxes = {}

		self.tempBoxStorage = {} # { id : box creation }
		self.editorMode = False
		self.selectingBox = False
		self.redrawing = False
		self.changingId = False
		self.gettingSecondId = False
		self.firstId = None
		self.secondId = None
		self.selectingBoxThreshold = 100

		# IDENTITIES
		self.lastSelectedId = None
		self.allInstances = {} # { id : instance }
		self.colorSetter = ColorSetter()
		self.idsHaveChanged = []

		# TEXT FILES
		self.frameswithboxes = []

	# Display
		# WINDOW
		self.window = Tk()
		self.window.title("Annotator")
		width = self.window.winfo_screenwidth()
		self.width = width
		self.img_width = width - self.leftPanelWidth - self.border # border on right = 10

		self.canvas = Canvas(master=self.window, width=self.width, height=self.height, relief='flat')
		self.window.minsize(self.width, self.height)

		# HEADER
		self.lbl_header = tk.Label(master=self.canvas,text="No file loaded")

		# TOOLBAR
		self.frm_toolbar = tk.Frame(master=self.canvas, height=10)
		self.btn_open = tk.Button(master=self.frm_toolbar, text="Open File", command=self.openDir)
		self.btn_next = tk.Button(master=self.frm_toolbar, text="Next Frame", command=self.btn_next)
		self.btn_prev = tk.Button(master=self.frm_toolbar, text="Prev Frame", command=self.btn_prev)
		self.btn_start = tk.Button(master=self.frm_toolbar, text="Start", command=self.start)
		self.btn_stop = tk.Button(master=self.frm_toolbar, text="Stop", command=self.stop)
		self.lbl_frameNum = tk.Label(master=self.frm_toolbar,text=" Frame Number: ")
		self.btn_open.grid(row=0, column=0)
		self.btn_next.grid(row=0, column=1)
		self.btn_prev.grid(row=0, column=2)
		self.btn_start.grid(row=0, column=3)
		self.btn_stop.grid(row=0, column=4)
		self.lbl_frameNum.grid(row=0, column=5)
		self.frm_toolbar.grid(row=1, column=0)

		# Main Elements
		# 		       Header
		#		      Tool Bar
		#            Main Frame
		#   LEFT PANEL (frm)   LABEL
		# |   edit buttons   | image |
		# | identities panel |       |
		# |    checkboxes    |       |
		self.frm_main = tk.Frame(master=self.canvas, width=10)
		self.frm_leftPanel = tk.Frame(master=self.frm_main)

		# LEFT PANEL (frm)
		# edit buttons
			# Draw New Box -- choose id in side panel, draw new box
			# Replace Box -- selectbox(), dialog = replace?, delete selected box, click again = draw new box
			# Change ID -- selectbox(), dialog = choose new id, update curr.boxes
				# selectbox() -- hover over box, highlight edge when over, click = select
			# Delete Box -- selectbox(), confirm dialog, update left panel

		# identities panel

		# checkboxes
			# Show Prev Frame Boxes -- checkbox (swaps to "hide")
			# Show Next Frame Boxes -- checkbox (swaps to "hide") -- need in case bird enters frame but isn't detected immediately

		# On next or finish drawing -- error if any boxes share an id, confirm boxes and curr.commitEdits

		# edit buttons
		self.frm_editor = tk.Frame(master=self.frm_leftPanel)
		self.btn_editAndSave = tk.Button(master=self.frm_editor, text="OPEN EDITOR", command=self.editAndSave, width=int(self.leftPanelWidth/10))
		self.btn_newBox = tk.Button(master=self.frm_editor, text="Create new box", command=self.newBox)
		self.btn_deleteBox = tk.Button(master=self.frm_editor, text="Delete box", command=self.deleteBox)
		self.btn_redrawBox = tk.Button(master=self.frm_editor, text="Redraw box", command=self.redrawBox)
		self.btn_changeId = tk.Button(master=self.frm_editor, text="Change box ID", command=self.changeId)
		self.btn_editAndSave.grid(sticky=N+W, row=0, column=0)
		self.frm_editor.grid(sticky=N+W, row=0, column=0)

		# identities panel
		self.frm_identities = tk.Frame(master=self.frm_leftPanel)
		self.lbl_allidheader = tk.Label(master=self.frm_identities,text=" All Identities")
		self.btn_newId = tk.Button(master=self.frm_identities, text="New ID", command=self.newId)
		self.listb_allIds = tk.Listbox(master=self.frm_identities, borderwidth=6, relief="flat", height=2 * self.leftPanelHeight_Row1, selectforeground="white", selectbackground="Black", activestyle="underline")


		# checkboxes

		# format
		self.frm_leftPanel.grid_rowconfigure(0, minsize=self.leftPanelHeight_Row0)
		self.frm_leftPanel.grid_rowconfigure(1, minsize=self.leftPanelHeight_Row1)
		self.frm_leftPanel.grid_rowconfigure(2, minsize=self.leftPanelHeight_Row2)


		# LABEL
		self.cvs_image = tk.Canvas(master=self.frm_main, width = self.width, height=self.height)

		self.frm_leftPanel.grid(row=0, column=0, sticky='nsew')
		self.cvs_image.grid(row=0,column=1, sticky='nsew')
		self.frm_main.grid_columnconfigure(0, minsize=self.leftPanelWidth)


	# Bindings
		# PLAYING VIDEO
		self.window.bind('<Left>', self.leftkey)
		self.window.bind('<Right>', self.rightkey)

		# BOUNDING BOXES
		# NOTE: Add undo button binding
		self.window.bind('<Escape>', self.key_esc)
		self.cvs_image.bind("<ButtonPress-1>", self.click)
		self.cvs_image.bind("<B1-Motion>", self.drag)
		self.cvs_image.bind("<ButtonRelease-1>", self.release)

		# IDENTITIES
		self.listb_allIds.bind('<<ListboxSelect>>', self.clickId)

	# Show
		self.lbl_header.grid(row=0, column=0)
		self.frm_toolbar.grid(row=1, column=0)
		self.frm_main.grid(row=2, column=0)
		self.canvas.grid_columnconfigure(0, weight=1)
		self.canvas.pack()
		self.window.mainloop()

# BOUNDING BOXES
	# IDENTITY PANEL
	def clickId(self, event):
		if not self.boxes.get(self.lastSelectedId) is None:
			self.setNaturalBox(self.lastSelectedId)
		w = event.widget
		index = int(w.curselection()[0])
		id = w.get(index).split(' ')[0]
		self.lastSelectedId = id
		box = self.curr.instances[id]

		if self.gettingSecondId:
			self.secondId = id
			self.gettingSecondId = False
			self.matchCurrBoxAndId()
		elif self.boxes.get(id) is not None:
			self.cvs_image.delete(self.boxes[id])
			self.boxes[id] = self.cvs_image.create_rectangle(box['x1'], box['y1'], box['x2'], box['y2'], outline=str(box['color']), width=7)

# EDITOR MODE
	# OPEN EDITOR
	def editAndSave(self):
		if not self.editorMode:
			self.editorMode = True
			self.btn_newBox.grid(sticky=N+W, row=1, column=0)
			self.btn_deleteBox.grid(sticky=N+W, row=2, column=0)
			self.btn_redrawBox.grid(sticky=N+W,row=3, column=0)
			self.btn_changeId.grid(sticky=N+W, row=4, column=0)

			self.frm_identities.grid(sticky=N+W, row=1, column=0)
			self.lbl_allidheader.grid(sticky=S+W, row=0, column=0)
			self.btn_newId.grid(sticky=N+E, row=0, column=1)
			self.listb_allIds.grid(sticky=N+W, row=1, column=0, columnspan = 2)

			self.loadNewFrame()
			self.btn_editAndSave.config(text="CLOSE EDITOR & SAVE")
		else:
			self.editorMode = False
			self.btn_newBox.grid_forget()
			self.btn_redrawBox.grid_forget()
			self.btn_changeId.grid_forget()
			self.btn_deleteBox.grid_forget()

			self.frm_identities.grid_forget()
			self.btn_editAndSave.config(text="OPEN EDITOR")

	# LEFT PANEL BUTTONS
	def newBox(self):
		if not self.boxes.get(self.lastSelectedId) is None:
			self.setNaturalBox(self.lastSelectedId)
		# self.penDown()
		# selectId(self)
		pass

	def deleteBox(self):
		if not self.boxes.get(self.lastSelectedId) is None:
			self.setNaturalBox(self.lastSelectedId)
		# self.penDown()
		# selectId(self)
		pass

	def redrawBox(self):
		if not self.boxes.get(self.lastSelectedId) is None:
			self.setNaturalBox(self.lastSelectedId)
		self.redrawing = True
		self.selectBox()

	def changeId(self):
		if not self.boxes.get(self.lastSelectedId) is None:
			self.setNaturalBox(self.lastSelectedId)
		self.changingId = True
		self.selectBox()

		# 1. select box
		# 2. select id
		# - new id: do the stuff done when parsing file
		# - old id: set curr_box = old id box (with new id and index), curr_id = new id
		#			matchCurrBoxAndId()
		#			set curr_box = old id box, curr_id = old id
		#			deletebox(old id) -> boxes.remove(old id), set old to white

		# selectBox()
		# dialog asking to (1) select another box on screen (2) select id in list or create new id
		# (1) -> swapId() PUT ONTO STACK TO RUN AT CONFIRM
		# (2) -> updateId()

	def selectBox(self):
		self.selectingBox = True
		for id in self.curr.instances.keys():
			self.cvs_image.delete(self.boxes[id])
			box = self.curr.instances[id]
			self.boxes[id] = self.cvs_image.create_rectangle(box['x1'], box['y1'], box['x2'], box['y2'], outline='red', width=5, activefill='red')
			self.cvs_image.tag_bind(self.boxes[id], '<Enter>', lambda event, a=id: self.markAsActiveBox(a))
			self.cvs_image.tag_bind(self.boxes[id], '<Leave>', lambda event, a=id: self.unmarkAsActiveBox(a))

	def markAsActiveBox(self, id):
		self.curr_id = id

	def unmarkAsActiveBox(self, id):
		self.curr_id = None

	def selectId(self):
		pass

	def newId(self):
		pass


	# DRAWING NEW BOX
	def setNaturalBox(self, id):
		if self.boxes.get(id) is not None:
			self.cvs_image.delete(self.boxes[id])
		box = self.curr.instances[id]
		self.boxes[id] = self.cvs_image.create_rectangle(box['x1'], box['y1'], box['x2'], box['y2'], outline=str(box['color']), width=2)

	def click(self, event):
		if self.drawing:
			self.curr_box = {"x1":0, "y1":0, "x2":0, "y2":0, "color":self.curr.instances[self.curr_id]['color']}
			self.curr_box['x1'], self.curr_box['y1'] = event.x, event.y
			self.rect = self.cvs_image.create_rectangle(event.x, event.y, event.x, event.y, outline=self.curr_box['color'], width=2)

	def drag(self, event):
		if self.drawing:
			self.cvs_image.coords(self.rect, self.curr_box['x1'], self.curr_box['y1'], event.x, event.y)

	def release(self, event):
		if self.drawing:
			if abs(event.x - self.curr_box['x1']) < self.minBoxSize or abs(event.y - self.curr_box['y1']) < self.minBoxSize:
				self.cvs_image.delete(self.rect)
			elif not self.topLevelOpen:
				self.curr_box['x2'], self.curr_box['y2'] = event.x, event.y
				self.saveOrCancel(event)

		if self.selectingBox:
			if self.curr_id is not None:
				for id in self.curr.instances.keys():
					self.setNaturalBox(id)

				if self.changingId:
					if self.gettingSecondId and self.curr_id is not self.firstId:
						self.secondId = self.curr_id
						self.gettingSecondId = False
						self.selectingBox = False
						self.matchCurrBoxAndId()
					else:
						self.firstId = self.curr_id
						self.gettingSecondId = True
						self.selectBox()

				elif self.redrawing:
					self.cvs_image.delete(self.boxes[self.curr_id])
					self.drawing = True
					self.selectingBox = False


	def saveOrCancel(self, event):
		self.topLevelOpen = True
		self.win = Toplevel()

		# Display
		self.win.geometry("+%d+%d" % (event.x, event.y))
		self.win.minsize(width=300, height=20)
		self.win.grid_columnconfigure(0, weight=1)
		self.win.grid_columnconfigure(1, weight=1)
		self.win.grid_rowconfigure(0, weight=1)
		self.win.grid_rowconfigure(1, weight=1)

		# Features
		self.win.title('New bounding box')
		message = "Coords: " + str(self.cvs_image.coords(self.rect)) + "    ID: "
		Label(self.win, text=message).grid(row=0, column=0, columnspan=23, sticky=W+E)
		Button(self.win, text='Cancel', command=self.btn_cancel).grid(row=1, column=0)
		Button(self.win, text='Confirm', command=self.btn_confirm).grid(row=1, column=1)

		# Window Cases
		self.win.protocol("WM_DELETE_WINDOW", self.miniClose)
		return self.saveBox

	def btn_cancel(self):
		self.cvs_image.delete(self.rect)
		self.rect = None
		self.win.destroy()
		self.topLevelOpen = False

	def btn_confirm(self):
		self.cvs_image.delete(self.rect)
		self.matchCurrBoxAndId()
		self.win.destroy()
		self.topLevelOpen = False

	def updateTempFrame(self, id):
		self.idsHaveChanged.append(id)
		if self.boxes.get(id) is not None:
			self.cvs_image.delete(self.boxes[id])
		i = self.allInstances[id]
		box = i.boxes[self.curr.frameNum]
		self.boxes[id] = self.cvs_image.create_rectangle(box['x1'], box['y1'], box['x2'], box['y2'], outline=i.color, width=2)

	def matchCurrBoxAndId(self):
		# TODO: Make all dialog boxes go through here
		if self.changingId:
			if self.boxes.get(self.secondId) is None: # id was chosen on left and is not on frame
				pass
			else: # both ids on screen
				a = self.allInstances[self.firstId]
				b = self.allInstances[self.secondId]
				a.swapId(b, self.curr.frameNum, self.frames) # update long term storage frames
				self.updateTempFrame(self.firstId) # update short term storage frame
				self.updateTempFrame(self.secondId)
			self.changingId = False


			# - new id: do the stuff done when parsing file
			# - old id: set curr_box = old id box (with new id and index), curr_id = new id
			#			matchCurrBoxAndId()
			#			set curr_box = old id box, curr_id = old id
			#			deletebox(old id) -> boxes.remove(old id), set old to white
		elif self.redrawing:
			id = self.allInstances[str(self.curr_id)]
			id.updateBoxes(self.curr_box, self.curr)
			self.updateTempFrame(self.curr_id)
			self.drawing = False
			self.redrawing = False

		self.curr_id = None


	# CASES
	def miniClose(self):
		self.btn_cancel()

	def key_esc(self, event):
		self.drawing = False
		if self.rect != None:
			self.cvs_image.delete(self.rect)

	# DISPLAY
	def leftkey(self, event):
		self.prev()

	def rightkey(self, event):
		self.next()

# OPENING FILE
	# ON LOAD
	def openDir(self):
		folder = tk.filedialog.askdirectory(title = "Select directory with video and text file")
		if folder is not "":
			for file in os.listdir(folder):
				if file.lower().endswith(".txt"):
					self.textFileName = str(folder + "/" + file)
				elif file.lower().endswith(".mp4"):
					self.videoFileName = str(folder + "/" + file)
		else:
			self.textFileName = "/Users/laurenkafkaloff/Desktop/Moon/TestData.txt"
			self.videoFileName = "/Users/laurenkafkaloff/Desktop/Moon/fewFrames.mp4"
		if not (self.textFileName is None or self.videoFileName is None):
			self.openVideo()

	def openVideo(self):
		self.video = cv2.VideoCapture(self.videoFileName)
		self.lbl_header.config(text=self.videoFileName)
		self.setDimsAndMultipliers()
		self.filling = True
		self.fillFiles()
		self.start()
		self.window.update()

	def setDimsAndMultipliers(self):
		# set dimensions
		self.ori_height = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
		self.ori_width = self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
		self.img_height = int(self.img_width/self.ori_width*self.ori_height)
		self.cvs_image.config(height=self.img_height)
		self.canvas.config(height=self.img_height + self.top_two_bars + self.border)
		self.window.minsize(self.width, self.img_height + self.top_two_bars + self.border)

		# find box multipliers
		self.boxMult = self.img_width / self.ori_width

	def videoLoop(self):
		try:
			while not self.stopEvent.is_set():
				if self.filling:
					self.fillVideoNext()
					# TODO: Load file (with progress) before video
					# if self.fileProg != 100:
					# 	print (self.fileProg)
					# else:
					# 	self.fillVideoNext()
				else:
					self.playing = True
					self.next()
		except RuntimeError as e:
			print("[INFO] caught a RuntimeError")

	def fillVideoNext(self):
		more, freeze = self.video.read()
		self.tempCount += 1
		if more:
			self.img = self.frameToImage(freeze)
			if self.tempCount >= len(self.frames): # file included no lines of instances on this frame
				self.f = Frame(frameNum=self.tempCount, img=self.img)
				self.frames.append(self.f)
			else:
				self.f = self.frames[self.tempCount]
				self.f.img = self.img
			self.loadNewBoxes()
		else: # finished loading
			self.stopEvent.set()
			self.filling = False
			self.curr = self.frames[1]
			self.loadNewFrame()

	def fillFiles(self):
		frm_index = 0
		id_index = 1
		box_index = 2

		# each frame stores identities with their boxes for quick access (short term storage)
		# each identity stores its frames with their boxes (long term storage)
		for line in open(self.textFileName, "r"):
			# data format: 1, 3, 794.27, 247.59, 71.245, 174.88, -1, -1, -1, -1
			textArray = line.split(",")
			a_frame = int(textArray[frm_index])
			a_id = str(textArray[id_index])

			# add frame if it doesn't exist yet
			if a_frame == len(self.frames):
				self.frames.append(Frame(frameNum=a_frame))

			x1 = float(textArray[box_index]) * self.boxMult # accounts for image resizing
			y1 = float(textArray[box_index + 1]) * self.boxMult
			x2 = x1 + float(textArray[box_index + 2]) * self.boxMult
			y2 = y1 + float(textArray[box_index + 3]) * self.boxMult
			box =  {"x1":x1, "y1":y1, "x2":x2, "y2":y2}

			# add new instance if this is its first frame/box
			if self.allInstances.get(a_id) is None:
				colorName, colorId = self.colorSetter.getColor()
				index = self.listb_allIds.size()
				self.listb_allIds.insert(END, str(a_id) + "   " + colorName)
				self.i = Instance(a_id, index, colorId)
				self.allInstances[a_id] = self.i
			box['color'] = self.allInstances[a_id].color

			# short term storage -- add box and id to frame storage
			self.frames[a_frame].addInstance(a_id, box)
			# long term storage -- add box to an existing instance's list of boxes
			self.allInstances[a_id].updateBoxes(box, self.frames[a_frame])

	def loadNewBoxes(self):
		instances = self.f.instances # { id: none }
		for id in instances.keys():
			instance = self.allInstances[id]
			box = instance.boxes[self.tempCount] # for each instance on the frame, get its corresponding box
			box['color'] = instance.color
			self.f.addInstance(id, box) # store box onto frame so you don't have to retreive it again

	def loadNewFrame(self):
		self.boxes = {}
		if not self.displayedImage is None:
			self.cvs_image.delete(self.displayedImage)
		self.displayedImage = self.cvs_image.create_image(0, 0, anchor="nw", image=self.curr.img) # load new image
		self.lbl_frameNum.config(text="Frame Number: " + str(self.curr.frameNum)) # load new frame number
		box = None
		if self.editorMode:
			for id in self.curr.instances.keys():
				if id in self.idsHaveChanged:
					if self.allInstances[id].boxes.get(self.curr.frameNum) is not None:
						self.curr.addInstance(id, self.allInstances[id].boxes[self.curr.frameNum])
					else:
						self.curr.removeInstance(id)
						continue
				box = self.curr.instances[id]
				self.boxes[id] = self.cvs_image.create_rectangle(box['x1'], box['y1'], box['x2'], box['y2'], outline=str(box['color']), width=2)
				self.listb_allIds.itemconfig(self.allInstances[id].index, bg=box['color'])
		else:
			for id in self.curr.instances.keys():
				if id in self.idsHaveChanged:
					box = self.allInstances[id].boxes[self.curr.frameNum]
				else:
					self.curr.removeInstance(id)
					continue
				box = self.curr.instances[id]
				self.cvs_image.create_rectangle(box['x1'], box['y1'], box['x2'], box['y2'], outline=str(box['color']), width=2)

	def frameToImage(self, freeze):
		rgb = cv2.cvtColor(freeze, cv2.COLOR_BGR2RGB)
		img = Image.fromarray(rgb)
		imgResized = img.resize((self.img_width, self.img_height), Image.NEAREST)
		return ImageTk.PhotoImage(imgResized)

	# PLAYING VIDEO
	def onLeavingFrame(self):
		if not self.playing:
			self.stop()

		if self.edited:
			commitEdits()

		if self.editorMode:
			for id in self.curr.instances.keys():
				self.listb_allIds.itemconfig(self.allInstances[id].index, bg='white')

	def next(self):
		if self.curr.frameNum == len(self.frames) - 1:
			return

		self.onLeavingFrame()
		self.curr = self.frames[self.curr.frameNum + 1]

		self.loadNewFrame()
		time.sleep(.01) # NOTE: Change sleep into a function of fps

	def prev(self):
		self.onLeavingFrame()
		if self.curr.frameNum > 1:
			self.curr = self.frames[self.curr.frameNum - 1]
			self.loadNewFrame()

	def start(self):
		if not self.video is None:
			self.stopEvent.clear()
			self.thread = threading.Thread(target=self.videoLoop, args=())
			self.thread.start()

			# NOTE: Set a callback to handle when the window is closed
			# self.window.wm_protocol("WM_DELETE_WINDOW", self.onClose)

	def stop(self):
		self.playing = False
		self.stopEvent.set()

	def commitEdits(self):
		pass
		# self.curr.commit() -- update self.curr.boxes to include the new boxes and identities
		# self.frames[self.curr.frameNum - 1] = self.curr
		# self.edited = False

	def btn_next(self):
		self.playing = False
		self.next()

	def btn_prev(self):
		self.playing = False
		self.prev()


	# WINDOW CASES
	def onClose(self):
		# NOTE: Save everything before closing entire window
		self.stop()

		# NOTE: Only load specified range of frames
		# LOAD A SPECIFIED RANGE OF FRAMES AHEAD OF TIME -- WHEN SWAPPINNG IDS, DON'T LOAD PAST THIS EITHER
