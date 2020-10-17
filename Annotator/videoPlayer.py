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
    self.bkdVideo = cv2.VideoCapture(self.videoFileName)
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
    self.width = self.window.winfo_width()
    self.height = self.window.winfo_height()
    temp_width = self.width - self.leftPanelWidth - self.border
    temp_height = self.height - self.dialog_height - self.playBar_height - self.border - 80
    wscale = temp_width / self.ori_width
    hscale = temp_height / self.ori_height
    self.scale = min(wscale, hscale)
    self.img_width = int(self.scale * self.ori_width)
    self.img_height = int(self.scale * self.ori_height)
    self.cvs_image.config(width=self.img_width, height=self.img_height)
    self.canvas.config(width=self.width, height=self.height)
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

    # slower playback rate if can't play real time
    self.rate = 1
    self.max_rate = 3

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
    # parse hour:min:sec and convert it into seconds
    ent_times = [int(tm) for tm in time.split(":")]
    seconds = ent_times[0]*3600 + ent_times[1]*60 + ent_times[2]
    return int(seconds * self.vid_fps)
    

def makePlayBar(self):
    self.play_w = self.img_width  # 1090
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

    if self.bar:
        self.cvs_playBar.coords(self.bar, self.play_0, self.play_1, self.play_2, self.play_3)
    else:
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
    if self.bar_head:
        self.cvs_playBar.coords(self.bar_head, line, self.play_1, line, self.play_3)
    else:
        self.bar_head = self.cvs_playBar.create_line(line, self.play_1, line, self.play_3)

    line = barFindLine(self, self.tail)
    if self.bar_tail:
        self.cvs_playBar.coords(self.bar_tail, line, self.play_1, line, self.play_3)
    else:
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
        if self.head - self.curr.frameNum > int(3*self.fwdSize/4):
            buffer_len = self.head - self.curr.frameNum + 600
            desired_buffer_len = int(3*self.fwdSize/4) + 600
            self.rate = min(self.rate*(buffer_len/desired_buffer_len), self.max_rate)
            #print("inc: {:.3f}, rate: {:.3f}".format(buffer_len/desired_buffer_len, self.rate))
            
            self.cvs_image.after(int(1000 / (self.rate * self.vid_fps)), periodicCall, self)
        else:
            buffer_len = self.head - self.curr.frameNum + 300
            desired_buffer_len = int(3*self.fwdSize/4) + 300
            self.rate = self.rate*(buffer_len/desired_buffer_len)
            #print("dec: {:.3f}, rate: {:.3f}".format(buffer_len/desired_buffer_len, self.rate))
            self.cvs_image.after(int(1000 / (self.rate * self.vid_fps)), periodicCall, self)
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
    # self.head = 0
    # self.tail = 0
    while True:
        # newstring = "head:{} tail:{} fn: {} fwdSize: {} bkdSize: {} fwdStop: {} bkdStop: {} num_frames: {}, filling: {}".format(
        #     self.head, self.tail, self.curr.frameNum, self.fwdSize, self.bkdSize, self.fwdStop, self.bkdStop,
        #     len(self.frames), self.filling)
        # if not self.printstring == newstring:
        #     print(newstring)
        #     self.printstring = newstring
        if self.stopChecker:
            self.stopChecker = False
            break
        if self.checking:
            self.checking = False
            num = self.curr.frameNum
            # NEXT CLICK
            while self.head - num < self.fwdSize and self.head < self.vid_totalFrames:
                more, freeze = self.video.read()
                #print("Checking: frame read at: {}".format(self.video.get(1)))
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
        if num - self.tail <= self.reloadBound and self.tail > 1: # self.tail != 0
            if self.bkdStop:
                #bkdReload(self, max(0, int(self.tail - self.bkdSize)), int(self.tail))
                bkdReload(self, max(0, int(num - self.bkdSize)), int(self.tail))

        if self.head - num >= self.fwdSize + self.bkdSize:
            if self.fwdStop:
                fwdReload(self, int(num + self.fwdSize), int(self.head))


def fwdReload(self, start=0, stop=0):
    #print("Reloading Forward")
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
    #video = cv2.VideoCapture(self.videoFileName)
    count = max(1, start)
    if not self.bkdStop:
        self.bkdVideo.set(1, start-1)
        while count <= stop:
            more, freeze = self.bkdVideo.read()
            self.img = frameToImage(self, freeze)
            self.frames[count].img = self.img
            self.loadNewBoxes(count)
            count += 1
        self.bkdStop = True
        self.tail = max(1, start)
        shiftHeadTail(self, self.curr.frameNum)
