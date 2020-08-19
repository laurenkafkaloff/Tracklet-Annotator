
from Annotator.videoPlayer import *


class barId(object):

    def __init__(self, id, top, s):
        self.s = s
        self.id = id.id
        self.instance = id
        self.top = top
        self.ends = []
        self.boxes = []

        frameNum = self.s.curr.frameNum
        self.updateEnds(frameNum)

    def updateEnds(self, frameNum):
        self.ends = []
        if len(self.instance.boxes) > 0:
            first = True
            prev = 0
            list = sorted(self.instance.boxes.keys())
            for i in list:
                if i == list[0]:
                    self.ends.append(i)
                elif i == list[-1]:
                    self.ends.append(i)
                else:
                    if i != prev + 1:
                        self.ends.append(prev)
                        self.ends.append(i)
                prev = i
            self.shift(frameNum)

    def shift(self, frameNum):
        if self.top:
            height = self.s.play_h * 3.5 / 12.0 + 10
        else:
            height = self.s.play_h * 8.5 / 12.0 + 10

        for box in self.boxes:
            self.s.cvs_playBar.delete(box)

        for i in range(0, len(self.ends) - 1, 2):
            tail = self.ends[i]
            head = self.ends[i + 1]
            if tail > frameNum + self.s.play_total_frames_on_bar / 2:
                break
            if head < frameNum - self.s.play_total_frames_on_bar / 2:
                continue
            tail = self.barFindLine(tail, frameNum)
            head = self.barFindLine(head, frameNum)
            self.boxes.append(self.s.cvs_playBar.create_rectangle(tail, height - 2.5, head,
                                                                  height + 2.5, fill=self.instance.color, outline="black", width=.2))

    def barFindLine(self, num, curr):
        middle = self.s.play_w / 2
        line = max(self.s.play_0, min(middle + self.s.play_x * (num - curr), self.s.play_2))
        return line
