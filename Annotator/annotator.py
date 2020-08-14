import tkinter as tk
from tkinter.ttk import *
from tkinter import *
from tkinter import filedialog, simpledialog
from PIL import ImageTk,Image
import time
import threading
import os
import shutil
import math
import copy
import cv2

from Annotator.frame import Frame
from Annotator.instance import Instance
from Annotator.colors import ColorSetter
from Annotator.video import *

class Annotator():
	# TODO: Account for edge cases
	# TODO: Load specified range of video
	# NOTE: Export environment into github

	def __init__(self):
	# Instance Variables
		# DISPLAY
		self.width, self.height = 960, 770 # width overwritten by screensize
		self.border = 10
		self.dialog_height = 45
		self.dialog_width = 600
		self.playBar_height = 55
		self.leftPanelWidth = 200
		self.leftPanelHeight_Editor = 170
		self.leftPanelHeight_Row1 = 10
		self.leftPanelHeight_Row2 = 50
		self.leftPanelHeight_Labeler = 120

		self.displayedIdent1Height = 15
		self.displayedIdent2Height = 15

		self.textFileName = None
		self.videoFileName = None
		self.checker = None
		self.firstVideo = True
		self.playThread = None
		self.bar = None
		self.bar_head = None
		self.bar_tail = None
		self.bar_id = None

	# Display
		# WINDOW
		self.window = Tk()
		self.window.title("Annotator")
		self.window.wm_protocol("WM_DELETE_WINDOW", self.onClose)
		width = self.window.winfo_screenwidth() - 150
		self.width = width
		self.img_width = width - self.leftPanelWidth - self.border # border on right = 10
		self.window.minsize(self.width, self.height)
		self.window.geometry(f"{self.width}x{self.height}")

		self.resetVariables()

		# 				     CANVAS
		#   LEFT PANEL (frm)           MAIN FRAME
		# |   edit boxes     | Header | Play Btns | Dialog
		# |   edit labels    |	         LABEL			   
		# | identity panel   | 			 image
		# |   checkboxes     |       	play bar
		# |   commit edits   |

		col_leftPanel = '#bebfc1'
		col_main = '#bebfc1'
		self.col_light ='#F0F0F0'


		# BASE
		self.canvas = Canvas(master=self.window, width=self.width, height=self.height, relief='flat', bg=col_main, highlightthickness=0)
		self.frm_main = tk.Frame(master=self.canvas, bg=col_main)
		self.frm_main.grid_columnconfigure(0, weight=1)
		self.frm_main.grid_rowconfigure(2, minsize=self.playBar_height)
		self.frm_leftPanel = tk.Frame(master=self.canvas, border=7)

		self.frm_leftPanel.grid(row=0, column=0, sticky='nsw')
		self.frm_main.grid(row=0, column=1, sticky="nswe")
		self.canvas.grid_columnconfigure(0, weight=1, minsize=self.leftPanelWidth)
		self.canvas.grid_columnconfigure(1, weight=1, minsize=self.width - self.leftPanelWidth)

		# LEFT PANEL
		# Edit Boxes
		self.frm_editor = tk.Frame(master=self.frm_leftPanel)
		self.lbl_editorHeader = tk.Label(master=self.frm_editor, text="Box Editor", bg=col_leftPanel, width=int(self.leftPanelWidth/10))
		self.btn_newBox = tk.Button(master=self.frm_editor, text="Create new box", command=self.newBox)
		self.btn_deleteBox = tk.Button(master=self.frm_editor, text="Delete box", command=self.deleteBox)
		self.btn_redrawBox = tk.Button(master=self.frm_editor, text="Redraw box", command=self.redrawBox)
		self.btn_changeId = tk.Button(master=self.frm_editor, text="Change box ID + Tracklet", command=self.changeId)
		self.lbl_editorHeader.grid(sticky=N+W, row=0, column=0)
		self.btn_newBox.grid(sticky=S+W, row=1, column=0)
		self.btn_deleteBox.grid(sticky=S+W, row=2, column=0)
		self.btn_redrawBox.grid(sticky=S+W,row=3, column=0)
		self.btn_changeId.grid(sticky=S+W, row=4, column=0)
		# Edit Labels
		self.frm_labeler = tk.Frame(master=self.frm_leftPanel)
		self.lbl_labelerHeader = tk.Label(master=self.frm_labeler, text="Label Editor", bg=col_leftPanel, width=int(self.leftPanelWidth/10))
		self.btn_label1 = tk.Button(master=self.frm_labeler, text="Button One", command=self.deleteBox)
		self.btn_label2 = tk.Button(master=self.frm_labeler, text="Button Two", command=self.redrawBox)
		self.lbl_labelerHeader.grid(sticky=N+W, row=0, column=0)
		self.btn_label1.grid(sticky=S+W,row=1, column=0)
		self.btn_label2.grid(sticky=S+W, row=2, column=0)
		# Identity Panel
		self.frm_identities = tk.Frame(master=self.frm_leftPanel, bg=col_leftPanel)
		self.lbl_allidheader = tk.Label(master=self.frm_identities, text=" All Identities", bg=col_leftPanel)
		self.btn_newId = tk.Button(master=self.frm_identities, text="New ID", command=self.newId, highlightbackground=col_leftPanel, border=3)
		self.list_ids = tk.Listbox(master=self.frm_identities, borderwidth=6, relief="flat", height=2 * self.leftPanelHeight_Row1, bg=self.col_light, selectforeground="blue", selectbackground=col_main, activestyle="underline")
		self.lbl_allidheader.grid(sticky=W+E, row=0, column=0)
		self.btn_newId.grid(sticky=N+E, row=0, column=1)
		self.list_ids.grid(sticky=N+W, row=1, column=0, columnspan = 2)
		# Checkboxes and commit
		self.frm_checkboxes = tk.Frame(master=self.frm_leftPanel)
		self.ckb_prev = tk.Checkbutton(master=self.frm_checkboxes, text="Show Previous Boxes", variable = self.p, command = self.showPrev)
		self.ckb_next = tk.Checkbutton(master=self.frm_checkboxes, text="Show Next Boxes", variable = self.n, command = self.showNext)
		self.btn_commmit = tk.Button(master=self.frm_checkboxes, text="Commit Edits", command=self.commitEdits)
		self.ckb_prev.grid(sticky=S+W, row=0, column=0)
		self.ckb_next.grid(sticky=S+W, row=1, column=0)
		self.btn_commmit.grid(sticky=S+W, row=2, column=0)
		# Place
		self.frm_editor.grid(sticky=N+W, row=0, column=0)
		self.frm_labeler.grid(sticky=N+W, row=1, column=0)
		self.frm_identities.grid(sticky=N+W, row=2, column=0)
		self.frm_checkboxes.grid(sticky=S+W, row=3, column=0)
		self.frm_leftPanel.grid_rowconfigure(0, minsize=self.leftPanelHeight_Editor)
		self.frm_leftPanel.grid_rowconfigure(1, minsize=self.leftPanelHeight_Labeler)

		# MAIN FRAME
		# Header
		self.frm_toolbar = tk.Frame(master=self.frm_main, bg=col_main)
		self.btn_open = tk.Button(master=self.frm_toolbar, text="Open File", command=self.openDir, highlightbackground=col_main, borderwidth=6)
		self.lbl_fileLoaded = tk.Label(master=self.frm_toolbar, text="  No file loaded", bg=col_main)
		self.lbl_fileFrames = tk.Label(master=self.frm_toolbar, text="  Total frames: ", bg=col_main)
		# self.lbl_fileTime = tk.Label(master=self.frm_toolbar, text="  Total length: ", bg=col_main)
		self.btn_open.grid(row=0, column=0, sticky=SW)
		self.lbl_fileLoaded.grid(row=1, column=0, sticky=NW)
		self.lbl_fileFrames.grid(row=2, column=0, sticky=NW)
		# self.lbl_fileTime.grid(row=3, column=0, sticky=NW)
		# Play Btns
		self.btn_next = tk.Button(master=self.frm_toolbar, text="Next Frame", command=self.btn_next, highlightbackground=col_main)
		self.btn_prev = tk.Button(master=self.frm_toolbar, text="Prev Frame", command=self.btn_prev, highlightbackground=col_main)
		self.btn_start = tk.Button(master=self.frm_toolbar, text="Start", command=self.playBtn, highlightbackground=col_main)
		self.btn_next.grid(row=0, column=1, sticky=SE)
		self.btn_prev.grid(row=1, column=1, sticky=NE)
		self.btn_start.grid(row=2, column=1, sticky=NE)
		# Dialog
		self.list_dialog = tk.Listbox(master=self.frm_toolbar, borderwidth=6, relief="flat", height=int(self.dialog_height/7), width=int(self.dialog_width/8), fg="black", bg=self.col_light, activestyle="none", font="Courier 11", selectforeground="blue", selectbackground=self.col_light)
		self.list_dialog.grid(row=0, column=2, rowspan=3, sticky=NE)
		# Image
		self.cvs_image = tk.Canvas(master=self.frm_main, width = self.width, height=self.height - 160, bg=col_main, highlightthickness=0, border=6)
		# Play Bar
		self.cvs_playBar = tk.Canvas(master=self.frm_main, width = self.width - self.leftPanelWidth, height=self.playBar_height, bg=col_main, highlightthickness=0, border=3)
		# Place
		self.frm_toolbar.grid_columnconfigure(0, minsize=300)
		self.frm_toolbar.grid_columnconfigure(1, minsize=300)
		self.frm_toolbar.grid_columnconfigure(2, minsize=self.width-800)
		self.frm_toolbar.grid(row=0, column=0, sticky=N+W+E)
		self.cvs_image.grid(row=1, column=0, sticky=N+W+E)
		self.cvs_playBar.grid(row=2, column=0, sticky=S+W+E, pady=0)


		self.lbl_frameNum = tk.Label(master=self.frm_main,text=" Frame Number: ")

		# PLAYING VIDEO
		self.window.bind('<Left>', self.leftkey)
		self.window.bind('<Right>', self.rightkey)
		self.window.bind('<space>', self.space)

		# BOUNDING BOXES
		# NOTE: Add undo button binding
		self.window.bind('<Escape>', self.key_esc)

		self.window.bind('<y>', self.confirm)
		self.window.bind('<n>', self.cancel)

		self.cvs_image.bind("<ButtonPress-1>", self.click)
		self.cvs_image.bind("<B1-Motion>", self.drag)
		self.cvs_image.bind("<ButtonRelease-1>", self.release)

		# IDENTITIES
		self.list_ids.bind('<<ListboxSelect>>', self.clickId)
		self.list_dialog.bind('<<ListboxSelect>>', self.doNothing)

		self.resetEditor()
		self.resetActions()

		self.canvas.pack()
		self.window.mainloop()

	def resetVariables(self):
		# FILLING VIDEO
		self.filling = False
		self.tempCount = 0
		self.fileProg = 0
		self.checking = False
		self.head = 0
		self.tail = 0
		self.fwdSize = 20
		self.bkdSize = 30
		self.reloadBound = 20
		self.fwdStop = True
		self.bkdStop = True
		self.stopChecker = False
		self.stopper = False
		# PLAYING VIDEO
		self.video = None
		self.playing = False
		self.frames = [Frame(frameNum=0)]
		self.curr = Frame(frameNum=0)
		self.displayedImage = None
		self.boxes = {}
		self.p = tk.IntVar()
		self.n = tk.IntVar()
		# BOUNDING BOXES / EDITOR
		self.minBoxSize = 10
		# IDENTITIES
		self.allInstances = {} # { id : instance }
		self.colorSetter = ColorSetter()
		self.idsHaveChanged = []
		self.maxId = -1
		# DIALOG
		self.dialogCount = 0

		if self.bar is not None:
			self.cvs_playBar.delete('all')

	def resetEditor(self):
		self.edited = False
		self.rect = None
		self.saveBox = None
		self.topLevelOpen = False
		self.boxes_prev = {}
		self.boxes_next = {}
		self.curr_box = {"x1":0, "y1":0, "x2":0, "y2":0}
		self.curr_id = None
		self.active_id = None
		self.firstId = None
		self.secondId = None
		self.lastSelectedId = None
		self.prev_on = False
		self.next_on = False
		self.showPrev()
		self.showNext()

	def resetActions(self):
		self.drawing = False
		self.selectingBox = False
		self.deletingBox = False
		self.redrawing = False
		self.newingBox = False
		self.changingId = False
		self.gettingSecondId = False
		self.waitingForClick = False
		self.openingVideo = False
		self.shifting = False

# EDITOR MODE
	def showPrev(self):
		if self.prev_on:
			self.prev_on = False
			if self.curr.frameNum - 1 >= 1:
				for id in self.frames[self.curr.frameNum - 1].instances.keys():
					box = self.allInstances[id].boxes[self.curr.frameNum - 1]
					self.boxes_prev[id] = self.cvs_image.create_rectangle(box['x1'], box['y1'], box['x2'], box['y2'], outline=str(box['color']), width=1)
					self.list_ids.itemconfig(self.allInstances[id].index, fg='red')
		else:
			self.prev_on = True
			for id in self.boxes_prev.keys():
				self.cvs_image.delete(self.boxes_prev[id])
				self.list_ids.itemconfig(self.allInstances[id].index, fg='black')
			self.boxes_prev = {}

	def showNext(self):
		if self.next_on:
			self.next_on = False
			if self.curr.frameNum + 1 < len(self.frames):
				for id in self.frames[self.curr.frameNum + 1].instances.keys():
					box = self.allInstances[id].boxes[self.curr.frameNum + 1]
					self.boxes_next[id] = self.cvs_image.create_rectangle(box['x1'], box['y1'], box['x2'], box['y2'], outline=str(box['color']), width=1)
					self.list_ids.itemconfig(self.allInstances[id].index, fg='green')
		else:
			self.next_on = True
			for id in self.boxes_next.keys():
				self.cvs_image.delete(self.boxes_next[id])
				self.list_ids.itemconfig(self.allInstances[id].index, fg='black')
			self.boxes_next = {}

	# LEFT PANEL BUTTONS
	# TODO: Esc undoes all button presses
	def newBox(self):
		if self.firstVideo:
			return
		self.resetActions()
		if not self.boxes.get(self.lastSelectedId) is None:
			self.setNaturalBox(self.lastSelectedId)
		self.addToDialog("Select an identity in the left panel")
		self.newingBox = True

	def deleteBox(self):
		if self.firstVideo:
			return
		self.resetActions()
		if not self.boxes.get(self.lastSelectedId) is None:
			self.setNaturalBox(self.lastSelectedId)
		self.addToDialog("Select a box to delete")
		self.deletingBox = True
		self.selectBox()

	def redrawBox(self):
		if self.firstVideo:
			return
		self.resetActions()
		if not self.boxes.get(self.lastSelectedId) is None:
			self.setNaturalBox(self.lastSelectedId)
		self.addToDialog("Select a box to redraw")
		self.redrawing = True
		self.selectBox()

	def changeId(self):
		if self.firstVideo:
			return
		self.resetActions()
		if not self.boxes.get(self.lastSelectedId) is None:
			self.setNaturalBox(self.lastSelectedId)
		self.addToDialog("Select a box to change the identity of")
		self.changingId = True
		self.selectBox()

	def selectBox(self):
		self.selectingBox = True
		for id in self.curr.instances.keys():
			self.cvs_image.delete(self.boxes[id])
			box = self.curr.instances[id]
			self.boxes[id] = self.cvs_image.create_rectangle(box['x1'], box['y1'], box['x2'], box['y2'], outline='red', width=5, activefill='red')
			self.cvs_image.tag_bind(self.boxes[id], '<Enter>', lambda event, a=id: self.markAsActiveBox(a))
			self.cvs_image.tag_bind(self.boxes[id], '<Leave>', lambda event, a=id: self.unmarkAsActiveBox(a))

	def markAsActiveBox(self, id):
		self.active_id = id

	def unmarkAsActiveBox(self, id):
		self.active_id = None

	def newId(self, a_id=None):
		if self.firstVideo:
			return
		if a_id is None:
			self.maxId = self.maxId + 1
			a_id = str(self.maxId)
		colorName, colorId = self.colorSetter.getColor()
		index = self.list_ids.size()
		self.list_ids.insert(END, str(a_id) + "   " + colorName)
		self.i = Instance(a_id, index, colorId, colorName)
		self.allInstances[a_id] = self.i
		self.list_ids.yview(END)

	def doNothing(self, event):
		pass

	def addToDialog(self, text, clickToConfirm=False):
		if self.dialogCount > 0:
			self.list_dialog.itemconfig(self.list_dialog.size() - 1, fg='#505050')
		self.list_dialog.insert(END, text)
		if clickToConfirm:
			self.waitingForClick = True
			self.list_dialog.insert(END, "Click Y to confirm")
			self.list_dialog.insert(END, "Click N to cancel")
			self.list_dialog.itemconfig(self.list_dialog.size() - 2, fg="green")
			self.list_dialog.itemconfig(self.list_dialog.size() - 1, fg="red")
		else:
			self.dialogCount += 1
		self.list_dialog.yview(END)
		self.list_dialog.selection_clear(0, END)

	def confirm(self, event):
		last = self.list_dialog.size() - 1
		msg = self.list_dialog.get(last - 2)[:-4] + ": Confirmed"
		self.list_dialog.delete(last)
		self.list_dialog.delete(last - 1)
		self.list_dialog.delete(last - 2)
		self.addToDialog(msg)

		if self.openingVideo:
			self.commitEdits()
			self.resetEditor()
			self.resetVariables()
			self.cvs_image.delete('all')
			if self.list_ids.size() != 0:
				self.list_ids.delete('0','end')
			openVideo(self)

		elif self.redrawing or self.newingBox:
			self.cvs_image.delete(self.rect)

		elif self.deletingBox:
			self.allInstances[self.curr_id].boxes.pop(self.curr.frameNum)
			self.curr.instances.pop(self.curr_id)
			self.updateTempFrame(str(self.curr_id))

		self.matchCurrBoxAndId()
		self.resetActions()

	def cancel(self, event):
		last = self.list_dialog.size() - 1
		msg = self.list_dialog.get(last - 2)[:-4] + ": Canceled"
		self.list_dialog.delete(last)
		self.list_dialog.delete(last - 1)
		self.list_dialog.delete(last - 2)
		self.addToDialog(msg)
		self.waitingForClick = False

		if self.openingVideo:
			self.resetEditor()
			self.resetVariables()
			self.cvs_image.delete('all')
			if self.list_ids.size() != 0:
				self.list_ids.delete('0','end')
			openVideo(self)

		if self.redrawing or self.newingBox:
			if self.redrawing:
				box = self.allInstances[str(self.curr_id)].boxes[self.curr.frameNum]
				self.boxes[str(self.curr_id)] = self.cvs_image.create_rectangle(box['x1'], box['y1'], box['x2'], box['y2'], outline=str(box['color']), width=3)
			self.cvs_image.delete(self.rect)
			self.rect = None

		elif self.changingId:
			print("ya")
			self.firstId = None
			self.secondId = None

		self.curr_id = None
		self.resetActions()

	# IDENTITY PANEL
	def clickId(self, event):
		if not self.boxes.get(self.lastSelectedId) is None:
			self.setNaturalBox(self.lastSelectedId)
		w = event.widget
		if w.curselection() == ():
			return
		index = int(w.curselection()[0])
		id = str(w.get(index).split(' ')[0])
		self.lastSelectedId = id

		if self.newingBox:
			if id not in self.boxes.keys(): # if not on frame -- wrong button otherwise
				self.curr_id = id
				self.addToDialog("Draw a box for ID #" + str(self.curr_id))
				self.drawing = True
			else:
				self.addToDialog("The selected identity is already on this frame -- please select again")

		elif self.gettingSecondId:
			for i in self.curr.instances.keys():
				self.setNaturalBox(i)
			if id is not self.firstId:
				self.secondId = id
				self.gettingSecondId = False
				self.selectingBox = False
				self.addToDialog("Swapping identity tracks for ID #" + str(self.firstId) + " and #" + str(self.secondId) + " ...", True)
			else:
				self.addToDialog("The selected identity was the same as the first identity -- please select again")
				self.selectBox()

		elif self.boxes.get(id) is not None: # highlight the selected box
			box = self.curr.instances[id]
			self.cvs_image.delete(self.boxes[id])
			self.boxes[id] = self.cvs_image.create_rectangle(box['x1'], box['y1'], box['x2'], box['y2'], outline=str(box['color']), width=7)

		barAddId(self, id)

	# DRAWING NEW BOX
	def setNaturalBox(self, id):
		if self.boxes.get(id) is not None:
			self.cvs_image.delete(self.boxes[id])
		box = self.curr.instances[id]
		self.boxes[id] = self.cvs_image.create_rectangle(box['x1'], box['y1'], box['x2'], box['y2'], outline=str(box['color']), width=3)

	def click(self, event):
		if self.drawing:
			self.curr_box = {"x1":0, "y1":0, "x2":0, "y2":0, "color":self.allInstances[self.curr_id].color}
			self.curr_box['x1'], self.curr_box['y1'] = event.x, event.y
			self.rect = self.cvs_image.create_rectangle(event.x, event.y, event.x, event.y, outline=self.curr_box['color'], width=3)

	def drag(self, event):
		if self.drawing:
			self.cvs_image.coords(self.rect, self.curr_box['x1'], self.curr_box['y1'], event.x, event.y)

	def release(self, event):
		if self.drawing:
			if abs(event.x - self.curr_box['x1']) < self.minBoxSize or abs(event.y - self.curr_box['y1']) < self.minBoxSize:
				self.cvs_image.delete(self.rect)
			elif not self.waitingForClick:
				self.curr_box['x2'], self.curr_box['y2'] = event.x, event.y
				if self.redrawing:
					self.addToDialog("Redrawing box from " + self.coordsToString(self.curr_box) + " for ID #" + self.curr_id + " ...", True)
				elif self.newingBox:
					self.addToDialog("Creating new box from " + self.coordsToString(self.curr_box) + " for ID #" + self.curr_id + " ...", True)

		if self.selectingBox:
			if self.active_id is not None:
				self.curr_id = str(self.active_id)
				for id in self.curr.instances.keys():
					self.setNaturalBox(id)

				if self.changingId:
					if self.gettingSecondId:
						if self.curr_id is not self.firstId:
							self.secondId = self.curr_id
							self.gettingSecondId = False
							self.selectingBox = False
							self.addToDialog("Swapping identity tracks for ID #" + str(self.firstId) + " and #" + str(self.secondId) + " ...", True)
						else:
							self.addToDialog("The selected identity was the same as the first identity -- please select again")
							self.selectBox()
					else:
						self.firstId = self.curr_id
						self.gettingSecondId = True
						self.addToDialog("Select an identity from the left panel or a box to swap with ID #" + str(self.curr_id))
						self.selectBox()

				elif self.redrawing:
					self.addToDialog("Draw new box for ID #" + str(self.curr_id))
					self.cvs_image.delete(self.boxes[self.curr_id])
					self.drawing = True
					self.selectingBox = False

				elif self.deletingBox:
					self.addToDialog("Deleting box for ID #" + str(self.curr_id) + " ...", True)
					self.selectingBox = False
			else:
				self.addToDialog("No box is currently highlighted - please select again")

	def coordsToString(self, box):
		return "(" + str(box['x1']) + ", " + str(box['y1']) + ") to (" + str(box['x2']) + ", " + str(box['y2']) + ")"

	def updateTempFrame(self, id):
		if self.boxes.get(id) is not None:
			self.cvs_image.delete(self.boxes[id])
		i = self.allInstances[id]
		if i.boxes.get(self.curr.frameNum) is not None:
			box = i.boxes[self.curr.frameNum]
			self.boxes[id] = self.cvs_image.create_rectangle(box['x1'], box['y1'], box['x2'], box['y2'], outline=i.color, width=3)
			self.list_ids.itemconfig(self.allInstances[id].index, bg=i.color)
		else:
			self.boxes.pop(id)
			self.list_ids.itemconfig(self.allInstances[id].index, bg=self.col_light)


	def matchCurrBoxAndId(self):
		# TODO: Make all dialog boxes go through here
		if self.changingId:
			a = self.allInstances[self.firstId]
			b = self.allInstances[self.secondId]
			a.swapId(b, self.curr.frameNum, self.frames, self.idsHaveChanged) # update long term storage frames
			self.updateTempFrame(self.firstId) # update short term storage frame
			self.updateTempFrame(self.secondId)

		elif self.redrawing or self.newingBox:
			id = self.allInstances[str(self.curr_id)]
			id.updateBoxes(self.curr_box, self.curr)
			self.updateTempFrame(self.curr_id)

		self.curr_id = None
		self.resetActions()

	# CASES
	def key_esc(self, event):
		self.drawing = False
		if self.rect != None:
			self.cvs_image.delete(self.rect)

	# DISPLAY
	def leftkey(self, event):
		self.prev()

	def rightkey(self, event):
		self.next()

	def space(self, event):
		self.playBtn()

# OPENING FILE
	# ON LOAD
	def openDir(self):
		folder = tk.filedialog.askdirectory(title = "Select directory with video and text file")
		if folder != "":
			videoFile = None
			for file in os.listdir(folder):
				if file.lower().endswith(".txt"):
					self.textFileName = os.path.join(folder, file)
				elif file.lower().endswith(".mp4"):
					videoFile = file[:-4]
					self.videoFileName = os.path.join(folder, file)

			directory = os.path.join(folder, "Edited Versions")
			if not os.path.exists(directory):
				os.mkdir(directory)
			file_count = len(os.listdir(directory))
			y = -1
			prev = None
			for file in os.listdir(directory):
				x = file.split("_")[-1][:-4]
				try:
					if int(x) > y:
						prev = os.path.join(directory, file)
						y = int(x)
				except ValueError:
					file_count -= 1
			if prev is None:
				prev = self.textFileName
			next = os.path.join(directory, videoFile + "_edited_" + str(file_count) + ".txt")
			self.file = next
			self.textFileName = prev

			if not (self.textFileName is None or self.videoFileName is None):
				self.openingVideo = True
				if self.firstVideo:
					self.firstVideo = False
					openVideo(self)
				else:
					self.addToDialog("Committing edits before loading a new video ...", True)

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
			if int(a_id) > self.maxId:
				self.maxId = int(a_id)

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
				self.newId(a_id)
			box['color'] = self.allInstances[a_id].color

			# short term storage -- add box and id to frame storage
			self.frames[a_frame].addInstance(a_id, box)
			# long term storage -- add box to an existing instance's list of boxes
			self.allInstances[a_id].updateBoxes(box, self.frames[a_frame])

	def loadNewBoxes(self, frame=None):
		if frame is None:
			frame = self.curr.frameNum
		f = self.frames[frame]
		instances = f.instances # { id: none }
		for id in instances.keys():
			instance = self.allInstances[id]
			box = instance.boxes[frame] # for each instance on the frame, get its corresponding box
			box['color'] = instance.color
			f.addInstance(id, box) # store box onto frame so you don't have to retreive it again

	def loadNewFrame(self):
		# new image
		if self.displayedImage is None:
			self.displayedImage = self.cvs_image.create_image(0, 0, anchor="nw", image=self.curr.img)
		else:
			# self.cvs_image.delete(self.displayedImage)
			# self.displayedImage = self.cvs_image.create_image(0, 0, anchor="nw", image = self.curr.img)
			self.cvs_image.itemconfig(self.displayedImage, image = self.curr.img)

		# new frame number
		self.lbl_frameNum.config(text="Frame Number: " + str(self.curr.frameNum))
		shiftBar(self, self.curr.frameNum)

		# update identity panel

		# reset elements
		for id in self.boxes.keys():
			self.cvs_image.delete(self.boxes[id])
			self.list_ids.itemconfig(self.allInstances[id].index, bg=self.col_light)
		self.boxes = {}

		# new boxes
		box = None
		removeInstances = []
		for id in self.curr.instances.keys():
			if id in self.idsHaveChanged:
				if self.allInstances[id].boxes.get(self.curr.frameNum) is not None:
					self.curr.addInstance(id, self.allInstances[id].boxes[self.curr.frameNum])
				else:
					removeInstances.append(id)
					continue
			box = self.curr.instances[id]
			self.boxes[id] = self.cvs_image.create_rectangle(box['x1'], box['y1'], box['x2'], box['y2'], outline=str(box['color']), width=3)
			self.list_ids.itemconfig(self.allInstances[id].index, bg=box['color'])
		for id in removeInstances:
			self.curr.removeInstance(id)

	# def frameToImage(self, freeze):
	# 	rgb = cv2.cvtColor(freeze, cv2.COLOR_BGR2RGB)
	# 	img = Image.fromarray(rgb)
	# 	imgResized = img.resize((self.img_width, self.img_height), Image.NEAREST)
	# 	return ImageTk.PhotoImage(imgResized)

	# PLAYING VIDEO
	def onLeavingFrame(self):
		if not self.playing:
			self.stop()

		# grey-out dialog
		last = self.list_dialog.size() - 1
		for i in range(0, self.dialogCount):
			self.list_dialog.itemconfig(last - i, fg="#BEBEBE")
		self.dialogCount = 0

		self.resetEditor()

	def next(self):
		if self.firstVideo:
			return
		if self.curr.frameNum < len(self.frames) - 1:
			self.checking = True
			# while self.filling:
			# 	time.sleep(.5)
			self.onLeavingFrame()
			self.curr = self.frames[self.curr.frameNum + 1]
			self.loadNewFrame()
			self.checking = True
			time.sleep(.001) # NOTE: Change sleep into a function of fps
		else:
			self.stop()
			self.addToDialog("Already on last frame")

	def prev(self):
		if self.firstVideo:
			return
		if self.curr.frameNum > 1:
			self.onLeavingFrame()
			self.curr = self.frames[self.curr.frameNum - 1]
			self.loadNewFrame()
			self.checking = True
		else:
			self.addToDialog("Already on first frame")

	def playBtn(self):
		if self.btn_start['text'] == "Start":
			self.btn_start.config(text="Stop")
			self.start()
		elif self.btn_start['text'] == "Stop":
			self.btn_start.config(text="Start")
			self.stop()
		else:
			print("error")

	def start(self):
		if not self.video is None:
			self.playing = True

	def stop(self):
		self.playing = False

	def btn_next(self):
		self.playing = False
		self.next()

	def btn_prev(self):
		self.playing = False
		self.prev()

	def commitEdits(self):
		self.addToDialog("Committing edits ...")
		self.commitEdits1()

	def commitEdits1(self):
		f = open(self.file, "w+")
		for frame in self.frames:
			for i in sorted(frame.instances.keys()):
				frameNum = int(frame.frameNum)
				id = str(i)
				box = self.allInstances[id].boxes[frameNum]
				top_x, top_y, b_width, b_height = round(box['x1']/self.boxMult, 2), round(box['y1']/self.boxMult, 2), round(abs(box['x2']-box['x1'])/self.boxMult, 2), round(abs(box['y2']-box['y1'])/self.boxMult, 2)
				f.write(",".join([str(frameNum), id, str(top_x), str(top_y), str(b_width), str(b_height)]) + "\n")
		f.close()
		last = self.list_dialog.size() - 1
		msg = self.list_dialog.get(last)[:-4] + ": Finished"
		self.dialogCount -= 1
		self.list_dialog.delete(last)
		self.addToDialog(msg)

	# WINDOW CASES
	def onClose(self):
		# NOTE: Save everything before closing entire window
		self.stopChecker = True
		self.window.destroy()

		# NOTE: Only load specified range of frames
		# LOAD A SPECIFIED RANGE OF FRAMES AHEAD OF TIME -- WHEN SWAPPINNG IDS, DON'T LOAD PAST THIS EITHER
		# Do go through the entire file and get the max id though
