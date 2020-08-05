import tkinter as tk
from tkinter import *  
from tkinter import filedialog
from PIL import ImageTk,Image  
import time
import threading

import moviepy
from moviepy.editor import VideoFileClip

import cv2


class Annotator():

	def __init__(self):
		self.width, self.height = 1000, 600
		self.video = None
		self.stopEvent = threading.Event()
		self.frames = []
		self.curr = (0, None)

		self.window = Tk()  
		self.window.title("Annotator")
		self.canvas = Canvas(master=self.window, width=self.width, height=self.height, relief=SUNKEN)
		self.window.minsize(self.width, self.height)

		# Create Header
		self.lbl_header = tk.Label(master=self.canvas,text="No file loaded")

		# Toolbar
		self.frm_toolbar = tk.Frame(master=self.canvas, height=10)
		self.btn_open = tk.Button(master=self.frm_toolbar, text="Open File", command=self.openDir)
		self.btn_next = tk.Button(master=self.frm_toolbar, text="Next Frame", command=lambda: self.next(False))
		self.btn_prev = tk.Button(master=self.frm_toolbar, text="Prev Frame", command=self.prev)
		self.btn_start = tk.Button(master=self.frm_toolbar, text="Start", command=self.start)
		self.btn_stop = tk.Button(master=self.frm_toolbar, text="Stop", command=self.stop)
		self.btn_open.grid(row=0, column=0)
		self.btn_next.grid(row=0, column=1)
		self.btn_prev.grid(row=0, column=2)
		self.btn_start.grid(row=0, column=3)
		self.btn_stop.grid(row=0, column=4)
		self.frm_toolbar.grid(row=1, column=0)

		self.window.bind('<Left>', self.leftkey)
		self.window.bind('<Right>', self.rightkey)

		# Image
		self.lbl_image = tk.Label(master=self.canvas)

		self.showElements()
		self.canvas.pack()
		self.window.mainloop()


	# DISPLAY
	def showElements(self):
		self.lbl_header.grid(row=0, column=0)
		self.frm_toolbar.grid(row=1, column=0)
		self.lbl_image.grid(row=2, column=0)

	def leftkey(self, event):
		self.prev()

	def rightkey(self, event):
		self.next(False)

	# OPENING VIDEO
	def openDir(self):
		fileTypes =  [('Videos', '*.mp4')]
		filename = tk.filedialog.askopenfilename(title = "Select file",filetypes = fileTypes)
		self.openVideo(filename)

	def openVideo(self, filename):
		self.video = cv2.VideoCapture(filename)
		self.lbl_header.config(text=filename)
		if self.video.isOpened():
			self.start()

		# self.video = VideoFileClip(filename)
		# rgb = self.video.get_frame(1)
		# img = Image.fromarray(rgb, 'RGB')
		# imgResized = image.resize((int(self.height/image.height*image.width), self.height), Image.NEAREST)
		# self.freeze = ImageTk.PhotoImage(imgResized)
		# self.lbl_image.config(image=self.freeze)
		# self.lbl_header.config(text=filename)

		#self.showElements()
		#self.canvas.update()
		self.window.update()
	def frameToImage(self, freeze):
		rgb = cv2.cvtColor(freeze, cv2.COLOR_BGR2RGB)
		img = Image.fromarray(rgb)
		imgResized = img.resize((int(self.height/img.height*img.width), self.height), Image.NEAREST)
		return ImageTk.PhotoImage(imgResized)


	# PLAYING VIDEO
	# TODO check if there's a vid
	def next(self, playing):
		print(len(self.frames), "   ", self.curr[0])
		if not playing:
			self.stop()
		if self.curr[0] == len(self.frames):
			more, freeze = self.video.read()
			if more:
				self.img = self.frameToImage(freeze)
				self.frames.append(self.img)
				self.curr = (self.curr[0] + 1, self.img)
				self.lbl_image.config(image=self.curr[1])
			else:
				print("video's over")
		else:
			self.curr = (self.curr[0] + 1, self.frames[self.curr[0]])
			self.lbl_image.config(image=self.curr[1])

	def prev(self):
		self.stop()
		if self.curr[0] > 1:
			self.curr = (self.curr[0] - 1, self.frames[self.curr[0] - 2])
			self.lbl_image.config(image=self.curr[1])

	def start(self):
		if self.video != None: 
			self.stopEvent.clear()
			self.thread = threading.Thread(target=self.videoLoop, args=())
			self.thread.start()

			# set a callback to handle when the window is closed
			# self.window.wm_protocol("WM_DELETE_WINDOW", self.onClose)

	def stop(self):
		self.stopEvent.set()

	def videoLoop(self):
		try:
			while not self.stopEvent.is_set():
				self.next(True)

		except RuntimeError as e:
			print("[INFO] caught a RuntimeError")

	def onClose(self):
		# TODO save everything before closing
		self.stop()
		




