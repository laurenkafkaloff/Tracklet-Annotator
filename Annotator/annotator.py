import tkinter as tk
from tkinter import *  
from tkinter import filedialog, simpledialog
from PIL import ImageTk,Image  
import time
import threading

from Annotator.frame import Frame
import cv2


class Annotator():
	# TODO: open folder instead of video so you can store original file and new file
	# TODO: export environment into github

	def __init__(self):
	# Instance Variables
		# DISPLAY
		self.width, self.height = 960, 600
		self.leftPanelWidth = 130

		# PLAYING VIDEO
		self.video = None
		self.stopEvent = threading.Event()
		self.playing = False
		self.frames = []
		self.curr = Frame(frameNum=0) #, img=None, boxes=None)
		self.displayedImage = None

		# BOUNDING BOXES
		self.idColors = ["white"] # colors for each index
		self.drawing = False
		self.edited = False
		self.rect = None
		self.minBoxSize = 10
		self.curr_box = {"x1":0, "y1":0, "x2":0, "y2":0, "id":None}
		self.curr_id = None
		self.btnSaveBox = None
		self.topLevelOpen = False

	# Display
		# Window
		self.window = Tk()  
		self.window.title("Annotator")
		self.canvas = Canvas(master=self.window, width=self.width, height=self.height, relief=SUNKEN)
		self.window.minsize(self.width, self.height)

		# Header
		self.lbl_header = tk.Label(master=self.canvas,text="No file loaded")

		# Toolbar
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
		#        Editor        Label
		# |   edit buttons   | image |
		# | identities panel |       |
		self.frm_main = tk.Frame(master=self.canvas, width=10)
		self.frm_editor = tk.Frame(master=self.frm_main)

		self.btn_draw = tk.Button(master=self.frm_editor, text="Start Drawing", command=self.draw)
		self.btn_draw.grid(row=0, column=0)
		self.cvs_image = tk.Canvas(master=self.frm_main, width = self.width, height=self.height)

		self.frm_editor.grid(row=0, column=0, sticky='nsew')
		self.cvs_image.grid(row=0,column=1, sticky='nsew')
		self.frm_main.grid_columnconfigure(0, minsize=self.leftPanelWidth)


	# Bindings
		# PLAYING VIDEO
		self.window.bind('<Left>', self.leftkey)
		self.window.bind('<Right>', self.rightkey)

		# BOUNDING BOXES
		self.window.bind('<Escape>', self.key_esc)
		self.cvs_image.bind("<ButtonPress-1>", self.click)
		self.cvs_image.bind("<B1-Motion>", self.drag)
		self.cvs_image.bind("<ButtonRelease-1>", self.release)

	# Show
		self.showElements()
		self.canvas.pack()
		self.window.mainloop()

	# BOUNDING BOXES
	def draw(self):
		if self.btn_draw['text'] == "Start Drawing":
			self.drawing = True
			self.curr_id = 0 # TODO: actually select identity
			self.btn_draw.config(text="Stop Drawing")
		else:
			self.drawing = False
			self.btn_draw.config(text="Start Drawing")

	def click(self, event):
		# select id first (or say new bird)
		if self.drawing:
			self.curr_box = {"x1":0, "y1":0, "x2":0, "y2":0, "id":None}
			self.curr_box['x1'], self.curr_box['y1'] = event.x, event.y
	
	def drag(self, event):
		if self.drawing:
			self.cvs_image.delete(self.rect)
			self.rect = self.cvs_image.create_rectangle(self.curr_box['x1'], self.curr_box['y1'], event.x, event.y, outline=self.idColors[self.curr_id], width=2)
		
	def release(self, event):
		if self.drawing and abs(event.x - self.curr_box['x1']) > self.minBoxSize and abs(event.y - self.curr_box['y1']) > self.minBoxSize:
			if not self.topLevelOpen:
				saveBox = self.saveBox(event)
			
			if saveBox:
				self.curr_box['x2'], self.curr_box['y2'] = event.x, event.y
				self.curr_box['id'] = self.curr_id
				self.curr.addBox(self.curr_box)
		if self.btn_draw['text'] == "Stop Drawing":
			self.drawing = True

		# TODO: give an option to cancel or save box when drag is finished
		

	def saveBox(self, event):
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
		message = "coords / identity"
		Label(self.win, text=message).grid(row=0, column=0, columnspan=23, sticky=W+E)
		Button(self.win, text='Cancel', command=self.btn_cancel).grid(row=1, column=0)
		Button(self.win, text='Confirm', command=self.btn_confirm).grid(row=1, column=1)

		# Window Cases
		self.win.protocol("WM_DELETE_WINDOW", self.miniClose)
		return self.btnSaveBox

	def btn_cancel(self):
		self.cvs_image.delete(self.rect)
		self.btnSaveBox = False
		self.rect = None
		self.win.destroy()
		self.topLevelOpen = False

	def btn_confirm(self):
		self.btnSaveBox = True
		self.win.destroy()
		self.topLevelOpen = False

	def miniClose(self):
		self.win.destroy()
		self.btn_cancel()

	def key_esc(self, event):
		self.drawing = False
		if self.rect != None:
			self.cvs_image.delete(self.rect)


	# DISPLAY
	def showElements(self):
		self.lbl_header.grid(row=0, column=0)
		self.frm_toolbar.grid(row=1, column=0)
		self.frm_main.grid(row=2, column=0)

	def leftkey(self, event):
		self.prev()

	def rightkey(self, event):
		self.next()

	# OPENING VIDEO
	def openDir(self):
		fileTypes =  [('Videos', '*.mp4')]
		filename = tk.filedialog.askopenfilename(title = "Select file",filetypes = fileTypes)
		self.openVideo(filename)

	def openVideo(self, filename):
		self.video = cv2.VideoCapture(filename)
		self.lbl_header.config(text=filename)
		self.start()
		self.stop()

		self.window.update()

	def frameToImage(self, freeze):
		rgb = cv2.cvtColor(freeze, cv2.COLOR_BGR2RGB)
		img = Image.fromarray(rgb)
		width = int(self.height/img.height*img.width)
		imgResized = img.resize((width, self.height), Image.NEAREST)
		return ImageTk.PhotoImage(imgResized)


	# PLAYING VIDEO
	# TODO check if there's a vid
	def next(self):
		if not self.playing:
			self.stop()

		if self.edited:
			commitEdits()

		if self.curr.frameNum == len(self.frames):
			more, freeze = self.video.read()
			if more:
				self.img = self.frameToImage(freeze)
				self.curr = Frame(frameNum=self.curr.frameNum + 1, img=self.img)
				self.frames.append(self.curr)
				self.lbl_frameNum.config(text="Frame Number: " + str(self.curr.frameNum))
				if self.displayedImage != None:
					self.cvs_image.delete(self.displayedImage)
				self.displayedImage = self.cvs_image.create_image(0, 0, anchor="nw", image=self.curr.img)
			else:
				print("video's over")
		else:
			self.curr = self.frames[self.curr.frameNum] 
			self.lbl_frameNum.config(text="Frame Number: " + str(self.curr.frameNum))
			if self.displayedImage != None:
				self.cvs_image.delete(self.displayedImage)
			self.displayedImage = self.cvs_image.create_image(0, 0, anchor="nw", image=self.curr.img)
			time.sleep(.1) # could make fps but this matches avg load time of a new/unloaded frame

	def prev(self):
		if not self.playing:
			self.stop()

		if self.edited:
			commmitEdits()

		if self.curr.frameNum > 1:
			self.curr = self.frames[self.curr.frameNum - 2]
			self.lbl_frameNum.config(text="Frame Number: " + str(self.curr.frameNum))
			if self.displayedImage != None:
				self.cvs_image.delete(self.displayedImage)
			self.displayedImage = self.cvs_image.create_image(0, 0, anchor="nw", image=self.curr.img)

	def start(self):
		if self.video != None: 
			self.playing = True
			self.stopEvent.clear()
			self.thread = threading.Thread(target=self.videoLoop, args=())
			self.thread.start()

			# set a callback to handle when the window is closed
			# self.window.wm_protocol("WM_DELETE_WINDOW", self.onClose)

	def stop(self):
		self.playing = False
		self.stopEvent.set()

	def videoLoop(self):
		try:
			while not self.stopEvent.is_set():
				self.next()

		except RuntimeError as e:
			print("[INFO] caught a RuntimeError")

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
		# TODO save everything before closing
		self.stop()
		




