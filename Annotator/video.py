from PIL import ImageTk,Image
import threading
import cv2
import time
import tkinter as tk

from Annotator.frame import Frame
from Annotator.instance import Instance
from Annotator.colors import ColorSetter

def openVideo(self):
	self.video = cv2.VideoCapture(self.videoFileName)
	setDimsAndMultipliers(self)
	self.lbl_fileLoaded.config(text=f"  File: {self.videoFileName.split('/')[-1]} ({self.vid_length})")
	self.lbl_fileFrames.config(text=f"  Total frames: {int(self.vid_totalFrames)}")
	self.filling = True
	self.fillFiles()

	if self.checker is not None:
		self.stopChecker = True
	self.checker = threading.Thread(target=checkThread, args=(self, ))
	self.checker.daemon = True
	self.checking = True
	self.checker.start()
	self.openingVideo = False

	if self.playThread is not None:
		self.stopper = True
	self.playThread = threading.Thread(target=playThread, args=(self, ))
	self.playThread.daemon = True
	self.playThread.start()

	self.window.update()

def setDimsAndMultipliers(self):
	# set dimensions
    self.ori_height = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    self.ori_width = self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.img_height = int(self.img_width/self.ori_width*self.ori_height)
    self.cvs_image.config(width=self.width, height=self.img_height)
    self.canvas.config(width=self.width, height=self.img_height + self.dialog_height + self.border)
    self.height = max(770, self.img_height + self.dialog_height + self.playBar_height + self.border + 60)
    self.window.minsize(self.width, self.height)
    self.window.geometry(f"{self.width}x{self.height}")

    # find box multipliers
    self.boxMult = self.img_width / self.ori_width

    # find video info
    self.vid_fps = self.video.get(cv2.CAP_PROP_FPS)
    self.vid_totalFrames =  self.video.get(cv2.CAP_PROP_FRAME_COUNT) - 1
    vid_seconds = self.vid_totalFrames/self.vid_fps
    vid_min = int(vid_seconds/60)
    vid_sec = int(vid_seconds - vid_min*60)
    self.vid_length = f"{vid_min} min {vid_sec} sec"

    makePlayBar(self)

def makePlayBar(self):
    self.play_w = self.cvs_image.winfo_width() #1090
    self.play_h = 15
    self.play_total_frames_on_bar = 100
    self.play_x = self.play_w/self.play_total_frames_on_bar
    self.cvs_playBar.config(width=self.play_w)

    self.cvs_playBar.create_line(self.play_w/2, self.play_h/2 + self.playBar_height/2 + 1, self.play_w/2, self.play_h/2 + self.playBar_height/2, arrow=tk.LAST)
    self.play_text = self.cvs_playBar.create_text(self.play_w/2, self.play_h/2 + self.playBar_height/2 + 16, text=f"Current Frame: {self.curr.frameNum}", font="TkDefaultFont 11")

    shiftBar(self, 0)

def shiftBar(self, frameNum):
    self.play_0 = max(self.play_w/2 - self.play_x * (frameNum-1), 0)
    self.play_1 = self.playBar_height/2 - self.play_h/2
    self.play_2 = min(self.play_w, self.play_w/2 + self.play_x * (self.vid_totalFrames-1) - self.play_x * (frameNum-1))
    self.play_3 = self.playBar_height/2 + self.play_h/2

    if self.bar is not None:
        self.cvs_playBar.delete(self.bar)
    self.bar = self.cvs_playBar.create_rectangle(self.play_0, self.play_1, self.play_2, self.play_3, fill='white', outline='black', width = 2)

    shiftHeadTail(self, frameNum)
    shiftId(self)

    self.cvs_playBar.itemconfig(self.play_text, text=f"Current Frame: {str(frameNum)}")

def barFindLine(self, num):
    middle = self.play_w/2
    line = max(self.play_0, min(middle + self.play_x * (num - self.curr.frameNum), self.play_2))
    return line

def shiftHeadTail(self, frameNum):
    if self.shifting:
        return
    self.shifting = True
    line = barFindLine(self, self.head)
    if self.bar_head is not None:
        self.cvs_playBar.delete(self.bar_head)
    self.bar_head = self.cvs_playBar.create_line(line, self.play_1, line, self.play_3)

    line = barFindLine(self, self.tail)
    if self.bar_tail is not None:
        self.cvs_playBar.delete(self.bar_tail)
    self.bar_tail = self.cvs_playBar.create_line(line, self.play_1, line, self.play_3)
    self.shifting = False

def barAddId(self, i):
    if self.bar_id is not None:
        self.cvs_playBar.delete(self.bar_id)

    id = self.allInstances[i]
    if len(id.boxes) > 0:
        # TODO: Allow for an id to leave the frame and come back (two separate lines) -- sort of the keys then look for gaps
        self.bar_id_first = min(id.boxes.keys())
        self.bar_id_last = max(id.boxes.keys())
        self.bar_id_color = id.color
        self.bar_id = 0
        shiftId(self)

def shiftId(self):
    if self.bar_id is None or self.bar_id_first == self.bar_id_last:
        return
    height = self.playBar_height/2
    self.cvs_playBar.delete(self.bar_id)
    self.bar_id = self.cvs_playBar.create_rectangle(barFindLine(self, self.bar_id_first), height-4, barFindLine(self, self.bar_id_last), height+2, fill=self.bar_id_color, outline="black", width=.2)

def frameToImage(self, freeze):
    rgb = cv2.cvtColor(freeze, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    imgResized = img.resize((self.img_width, self.img_height), Image.NEAREST)
    return ImageTk.PhotoImage(imgResized)

def playThread(self):
    while True:
        if self.stopper:
            self.stopper = False
            break
        if self.playing and not self.filling:
            self.next()

def checkThread(self):
    self.head = 0
    self.tail = 0
    while True:
        if self.stopChecker:
            self.stopChecker = False
            break
        if self.checking:
            self.checking = False
            num = self.curr.frameNum
        # NEXT CLICK
            # shift window head forward one frame
            while self.head - num < self.fwdSize and self.head < self.vid_totalFrames:
                more, freeze = self.video.read()
                if more:
                    self.head += 1
                    self.img = frameToImage(self, freeze)
                    if self.head >= len(self.frames): # file included no lines of instances on this frame
                        self.f = Frame(frameNum=self.head, img=self.img)
                        self.frames.append(self.f)
                    else:
                        self.f = self.frames[self.head]
                        self.f.img = self.img
                    self.loadNewBoxes(self.head)
            if self.filling:
                self.filling = False
                self.next()

            # shift window tail forward one frame
            while num - self.tail > self.bkdSize:
                self.frames[self.tail].img = None
                self.tail += 1

        # PREV CLICK
            # reload video if too close to window tail
            if num - self.tail <= self.reloadBound and self.tail != 0:
                if self.bkdStop:
                    bkdReload(self, max(0, int(self.tail - self.bkdSize)), int(self.tail))
            # reload video if too far from window head
            if self.head - num >= self.fwdSize + self.bkdSize:
                if self.fwdStop:
                    fwdReload(self, int(num + self.fwdSize), int(self.head))

def fwdReload(self, start=0, stop=0):
    self.fwdStop = False
    if not self.fwdStop:
        self.video.set(1, start)
        for i in range(start + 1, stop):
            if i in self.frames:
                self.frames[i].img = None
        self.fwdStop = True
        self.head = start
        shiftHeadTail(self, self.curr.frameNum)


def bkdReload(self, start=0, stop=0):
    self.bkdStop = False
    video = cv2.VideoCapture(self.videoFileName)
    count = start
    if not self.bkdStop:
        video.set(1, start - 1)
        while count < stop:
            more, freeze = video.read()
            self.img = frameToImage(self, freeze)
            self.frames[count].img = self.img
            self.loadNewBoxes(count)
            count += 1
        self.bkdStop = True
        self.tail = start
        shiftHeadTail(self, self.curr.frameNum)
