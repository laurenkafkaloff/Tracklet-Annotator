from PIL import ImageTk, Image
import threading
import cv2
import time
import tkinter as tk
import queue

from Annotator.frame import Frame
from Annotator.instance import Instance
from Annotator.colors import ColorSetter
from Annotator.barId import barId


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
    self.window.update()

def setDimsAndMultipliers(self):
    # set dimensions
    self.ori_height = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    self.ori_width = self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.img_height = int(self.img_width / self.ori_width * self.ori_height)
    self.cvs_image.config(width=self.width, height=self.img_height)
    self.canvas.config(width=self.width, height=self.img_height + self.dialog_height + self.border)
    self.height = max(770, self.img_height + self.dialog_height + self.playBar_height + self.border + 60)
    self.window.minsize(self.width, self.height)
    self.window.geometry(f"{self.width}x{self.height}")

    # find box multipliers
    self.boxMult = self.img_width / self.ori_width

    # find video info
    self.vid_fps = self.video.get(cv2.CAP_PROP_FPS)
    self.vid_totalFrames = self.video.get(cv2.CAP_PROP_FRAME_COUNT) - 1
    vid_seconds = self.vid_totalFrames / self.vid_fps
    vid_min = int(vid_seconds / 60)
    vid_sec = int(vid_seconds - vid_min * 60)
    self.vid_length = f"{vid_min} min {vid_sec} sec"

    makePlayBar(self)

def getTime(self, frame):
    vid_seconds = frame / self.vid_fps
    vid_hour = int(vid_seconds / 3600)
    vid_min = int((vid_seconds - vid_hour * 60) / 60)
    vid_sec = int(vid_seconds - vid_min * 60 - vid_hour * 60)
    vid_hour_str = "{:02d}".format(vid_hour)
    vid_min_str = "{:02d}".format(vid_min)
    vid_sec_str = "{:02d}".format(vid_sec)
    return f"{vid_hour_str}:{vid_min_str}:{vid_sec_str}"

def getFrame(self, time):
    ###############################
    seconds = None # parse hour:min:sec and convert it into seconds
    return seconds * self.vid_fps

def makePlayBar(self):
    self.play_w = self.cvs_image.winfo_width()  # 1090
    self.play_h = self.playBar_height / 2 + 15 / 2 - 10
    self.play_total_frames_on_bar = 100
    self.play_x = self.play_w / self.play_total_frames_on_bar
    self.cvs_playBar.config(width=self.play_w)

    self.cvs_playBar.create_line(self.play_w / 2, self.play_h + 11, self.play_w / 2, self.play_h + 10, arrow=tk.LAST)
    self.play_text = self.cvs_playBar.create_text(self.play_w / 2, self.play_h + 26,
                                                  text=f"Current Frame: {self.curr.frameNum}", font="TkDefaultFont 11")

    shiftBar(self, 0)


def shiftBar(self, frameNum):
    self.play_0 = max(self.play_w / 2 - self.play_x * (frameNum - 1), 0)
    self.play_1 = 10
    self.play_2 = min(self.play_w, self.play_w / 2 + self.play_x * (self.vid_totalFrames - 1) - self.play_x * (frameNum - 1))
    self.play_3 = self.play_1 + self.play_h

    if self.bar is not None:
        self.cvs_playBar.delete(self.bar)
    self.bar = self.cvs_playBar.create_rectangle(self.play_0, self.play_1, self.play_2, self.play_3, fill='white', outline='black', width=2)

    shiftHeadTail(self, frameNum)

    if self.bar_id_top is not None:
        self.bar_id_top.shift(frameNum)
    if self.bar_id_bottom is not None:
        self.bar_id_bottom.shift(frameNum)

    self.cvs_playBar.itemconfig(self.play_text, text=f"Current Frame: {str(frameNum)}")


def barFindLine(self, num):
    middle = self.play_w / 2
    line = max(self.play_0, min(middle + self.play_x * (num - self.curr.frameNum), self.play_2))
    return line


def shiftHeadTail(self, frameNum):
    line = barFindLine(self, self.head)
    if self.bar_head is not None:
        self.cvs_playBar.delete(self.bar_head)
    self.bar_head = self.cvs_playBar.create_line(line, self.play_1, line, self.play_3)

    line = barFindLine(self, self.tail)
    if self.bar_tail is not None:
        self.cvs_playBar.delete(self.bar_tail)
    self.bar_tail = self.cvs_playBar.create_line(line, self.play_1, line, self.play_3)


def barAddId(self, i):
    id = self.allInstances[i]
    if self.bar_id_top is None:
        self.bar_id_top = barId(id, True, self)
    elif self.bar_id_bottom is None and self.bar_id_top.id != i:
        self.bar_id_bottom = barId(id, False, self)
    elif self.bar_id_top.id != i and self.bar_id_bottom.id != i:
        if self.top:
            self.top = False
            for box in self.bar_id_top.boxes:
                self.cvs_playBar.delete(box)
            self.bar_id_top = barId(id, True, self)
        else:
            self.top = True
            for box in self.bar_id_bottom.boxes:
                self.cvs_playBar.delete(box)
            self.bar_id_bottom = barId(id, False, self)


def frameToImage(self, freeze):
    rgb = cv2.cvtColor(freeze, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    imgResized = img.resize((self.img_width, self.img_height), Image.NEAREST)
    return ImageTk.PhotoImage(imgResized)


def periodicCall(self):
    processIncoming(self)
    if self.playing:
        self.cvs_image.after(int(1000 / self.vid_fps), periodicCall, self)
    else:
        self.queue = queue.Queue()


def processIncoming(self):
    if not self.queue.empty():
        try:
            self.queue.get(0)
            self.next()
        except:
            pass
    else:
        self.list_dialog.yview(0)


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
            while self.head - num < self.fwdSize and self.head < self.vid_totalFrames:
                more, freeze = self.video.read()
                if more:
                    self.head += 1
                    self.img = frameToImage(self, freeze)
                    # file included no lines of instances on this frame
                    if self.head >= len(self.frames):
                        self.f = Frame(frameNum=self.head, img=self.img)
                        self.frames.append(self.f)
                    else:
                        self.f = self.frames[self.head]
                        self.f.img = self.img
                        self.loadNewBoxes(self.head)
                if self.filling:
                    self.filling = False
                    self.next()

            while num - self.tail > self.bkdSize:
                self.frames[self.tail].img = None
                self.tail += 1

        # PREV CLICK
        if num - self.tail <= self.reloadBound and self.tail != 0:
            if self.bkdStop:
                bkdReload(self, max(0, int(self.tail - self.bkdSize)), int(self.tail))

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
