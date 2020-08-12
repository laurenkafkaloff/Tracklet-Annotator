from PIL import ImageTk,Image
import threading
import cv2
import time

def frameToImage(self, freeze):
    rgb = cv2.cvtColor(freeze, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    imgResized = img.resize((self.img_width, self.img_height), Image.NEAREST)
    return ImageTk.PhotoImage(imgResized)

def checkThread(self):
    self.head = 0
    self.tail = 0
    while True:
        if self.stopChecker:
            self.stopChecker = False
            break
        if self.checking:
            # print(f"tail: {self.tail}   curr: {self.curr.frameNum}   head: {self.head}   fwd: {self.fwdStop}   bkd: {self.bkdStop}")
            self.checking = False
            num = self.curr.frameNum
            # NEXT CLICK
            # shift window head forward one frame
            while self.head - num < self.fwdSize and self.head < self.vid_totalFrames - 1:
                # print(f"head: {self.head}   curr: {num}")
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

            # for frm in self.frames:
            #     print(str(frm.frameNum) + ": " + str(frm.img is None))

            # shift window tail forward one frame
            while num - self.tail > self.bkdSize:
                self.frames[self.tail].img = None
                self.tail += 1

        # PREV CLICK - perhaps merge these two cases
            # reload video if too close to window tail
            if num - self.tail <= self.reloadBound and self.tail != 0:
                if self.bkdStop:
                    bkdReload(self, max(0, int(self.tail - self.bkdSize)), int(self.tail))
            # reload video if too far from window head
            if self.head - num >= self.fwdSize + self.bkdSize:
                self.addToDialog("4")
                if self.fwdStop:
                    fwdReload(self, int(num + self.fwdSize), int(self.head))

def fwdReload(self, start=0, stop=0):
    self.fwdStop = False
    if not self.fwdStop:
        self.addToDialog("41")
        self.video.set(1, start)
        for i in range(start + 1, stop):
            if i in self.frames:
                self.frames[i].img = None
        self.fwdStop = True
        self.head = start


def bkdReload(self, start=0, stop=0):
    self.bkdStop = False
    video = cv2.VideoCapture(self.videoFileName)
    count = start
    if not self.bkdStop:
        self.addToDialog("31")
        video.set(1, start - 1)
        while count < stop:
            more, freeze = video.read()
            self.img = frameToImage(self, freeze)
            self.frames[count].img = self.img
            self.loadNewBoxes(count)
            count += 1
        self.bkdStop = True
        self.tail = start
