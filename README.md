# Tracklet Annotator
Tracklet Annotator is a bounding box annotation tool for modifying auto-generated instance tracks on videos. It is written in Python and uses Tkinter for the graphical interface and OpenCV for video processing. 

The tool is intended to be used after a multi-object track finding algorithm has  already been applied, and thus takes in a video and text file containing frame-level bounding box coordinates as input. That being said, it can also be used to manually draw and label tracks without prior detection.

### Features
* [ ]
* [ ]
* [ ]


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the following modules via terminal:

```bash
pip install [ ]
pip install [ ]
pip install [ ]
```
Download or clone [Tracklet-Annotator](https://github.com/laurenkafkaloff/Tracklet-Annotator). Launch the program by moving into the directory named **Tracklet-Annotator-master** and running the following command:
```bash
python3 -m Annotator
```
## Usage

### Formatting Data
The program takes in a __directory containing a video and text file__ as input. Any modifications made to the tracks will be stored in this directory as a new file and be automatically applied when reopening the video for further edits.
> For an example, explore the files in Tracklet-Annotator/Example-Directory/Edited-Versions
#### VALID INPUT
_Video file types_ —  *.mp4, *.mov, *.avi, *.mpeg

_Text file type_ — *.txt

_Text format_ — each line denotes one frame-level object instance as structured below
```bash
<frame>, <id>, <bb_left>, <bb_top>, <bb_width>, <bb_height> (optional: <conf>)
```
* Null fields (id, conf) should be listed as -1
* <bb_left>, <bb_top> = upper-left coordinate of bounding box
* <conf> =  the detection confidence of the auto-generated boxes (set to 1 for any manually drawn boxes)
* __Store an empty text file in the directory if no prior detections were made__
#### OUTPUT FORMAT
The output is structured similarly, with both null fields listed as -1 if necessary. The top of the file may include several lines to store customized ID names and colors. The lines are structured as follows:
 ```bash
* <id>, <color>, <name>
```
* If only color OR name is customized, the default element is stored as "None"

### Playing Video
Start by clicking "Open Directory" to select the directory containing your desired video and text. file
* Skip through frames — Prev: <left-key> | Next: <right-key> | Start/Stop: <space>
* Check loaded frames — The play bar on the bottom draws zero to two thin vertical lines to signal which frames are currently loaded and stored. The window is set to fifty frames and can be modified to preserve/sacrifice memory by changing the following variables:
```bash
self.fwdSize, self.bkdSize = 20, 30
```

_Bug: Occassionally frame data and displayed images will become offset by one. To fix, commit changes (described below) and reopen video._
 
### Editing Bounding Boxes & Tracklets

### Editing Identities

### Committing Changes


