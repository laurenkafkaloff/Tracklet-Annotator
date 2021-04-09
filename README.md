# Tracklet Annotator
Tracklet Annotator is a bounding box annotation tool for modifying and correcting auto-generated instance tracks on videos. It is written in Python and uses Tkinter for the graphical interface and OpenCV for video processing. 

The tool is intended to be used after a multi-object track finding algorithm (_to be implemented_) has already been applied, and thus takes in a video and text file containing frame-level bounding box coordinates as input. That being said,it can also be used to manually draw and label tracks without prior detection.

### Features
* Drawing tool for creating and deleting bounding boxes
* Memory-efficient video player for frame-level analysis
* Built-in dialog box for displaying instructions, tracking progress, and confirming edits
* Functions to handle identity swaps and tracklet merging
* Play bar to display and compare when zero to two identities appear in frame 
* Option for customizing identity names and colors

[![Demo1.png](https://i.postimg.cc/zBNdd3q0/Demo1.png)](https://postimg.cc/Tykq1dLD)

### Live Demo: [ ]
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
## Formatting Data
The program takes in a __directory containing a video and text file__ as input. Any modifications made to the tracks will be stored in this directory as a new file and be automatically applied when reopening the video for further edits.

For an example, explore the files in Tracklet-Annotator/Example-Directory/Edited-Versions
### Valid Input
* __Video file types__ —  *.mp4, *.mov, *.avi, *.mpeg

* __Text file type__ — *.txt

* __Text format__ — each line denotes one frame-level object instance as structured below
   * Null fields (id, conf) should be listed as -1
   * <bb_left>, <bb_top> = top-left coordinate of bounding box
   * \<conf\> =  the detection confidence of the auto-generated boxes (set to 1 for any manually drawn boxes)
  * __Store an empty text file in the directory if no prior detections were made__
```bash
<frame>, <id>, <bb_left>, <bb_top>, <bb_width>, <bb_height> (optional: <conf>)
```
### Output Format
The output is structured similarly, with both null fields listed as -1 if necessary. The top of the file may include several lines to store customized ID names and colors. The line structure is shown below.

* If only color OR name is customized, the default element is stored as "None"
 ```bash
* <id>, <color>, <name>
```

## Playing Video
Start by clicking "Open Directory" to select the directory containing your desired video and text file.

* __Skip through frames__ — Prev: \<left-key\> | Next: \<right-key\> | Start/Stop: \<space\>
* __Check loaded frames__ — The play bar on the bottom draws zero to two thin vertical lines to signal which frames are currently loaded and stored. The window is set to fifty frames and can be modified to preserve/sacrifice memory by changing the following variables:
```bash
self.fwdSize, self.bkdSize = 20, 30
```
_Bug: Occassionally frame data and displayed images will become offset by one. To fix, commit changes (described below) and reopen video._
 
## Editing Bounding Boxes
All button instructions and confirmations are printed in the built-in dialog box (top-right corner) when applicable. Supplementary details are written below to explain each button's purpose and full functionality.
### Button Descriptions
* __Create New Box__ — No two boxes can have the same identity on a given frame, so creating a new box involves adding a new identity to the frame. After clicking "Create new box," you will be instructed to select an uncolored identity from the lefthand panel. Select a listed ID to add to a pre-existing track or create a "New ID" to start an entirely new track. Once a valid ID is selected, the dialog will direct you to draw a box for the ID. Click and drag your cursor on the canvas to create a box (dragging from either corner will properly save as top-left to bottom-right). 

* __Delete Box__ — Selecting "Delete box" will highlight all present boxes. Hover over the edge of the desired box and click when it is filled.

* __Redraw Box__ — This button combines "Delete" → "Create new" in order to make it easier to perfect the outline of boxes on correctly detected identities.

[![](https://i.postimg.cc/ZKD6xvMP/ezgif-com-video-to-gif-1.gif)](https://postimg.cc/D8LW20Fm)

* __Cancel__ — The cancel button and \<esc\> terminate all current actions at any time. 
* __Show Previous/Next Boxes__ — Selecting these checkboxes will thinly draw previous/next-frame boxes onto the current frame. It will also highlight the appearing IDs in red/green in the identities panel. The purpose of this feature is to ease the process of drawing when the initial appearance or final frame of an instance's track is missed.

## Editing Identities and Tracks
The identities panel displays all existing identities in order of appearance. Each ID has a unique key that cannot be edited and an auto-generated or user-specified color. IDs are colored if they appear on the current frame and are white otherwise.

Note that features and buttons involving tracks are most helpful once the bounding boxes have already been reviewed and corrected. Thus it is recommended to perfect boxes prior to merging or swapping tracks.
### Visual Features
* __Highlight an ID's box__ — Select a colored ID to create a thick outline on its corresponding box

[![ezgif-com-video-to-gif-3.gif](https://i.postimg.cc/mkWTsjk3/ezgif-com-video-to-gif-3.gif)](https://postimg.cc/BLpr5xxt)

* __Display ID's full segmented track__ — Select any ID to have the play bar display when the instance is (or is not) in frame

* __Compare two tracks__ — Select two IDs to compare when the two instances are in frame. Auto-generated tracks will categorize an object that leaves and re-enters a frame as two separate instances. These instances will have no overlapping frames (as they are the same object) and their tracks will eventually want to be merged. It is for this scenario that this feature is most helpful.

[![](https://i.postimg.cc/wj2MQCvC/ezgif-com-video-to-gif-2.gif)](https://postimg.cc/yDJ7Vr0j)

### Button Descriptions
* __Swap Track IDs__ — This button will swap two tracks starting from the current frame. That is, all prior bounding boxes will maintain their current identity while all following will switch to the other. When one instance gets in the way of another, it is common for auto-generated tracks to mistakenly swap their identities once the occlusion subsides. This results in a consecutive series of frames with misidentified boxes. To make the most out of this feature, go to the initial frame when the tracks are swapped and then apply it. 

_Below are some examples of swapping tracks [A] and [B] (let the vertical line mark the current frame)_
``` bash
BEFORE                             BEFORE                          BEFORE
[A]:      |---                     [A]: -----|---  ---             [A]: |----------     
[B]: --   |      ------            [B]:    --|--------             [B]: |
          |                                  |                          |
AFTER     |                        AFTER     |                     AFTER|
[A]:      |      ------            [A]: -----|--------             [A]: |        
[B]: --   |---                     [B]:    --|---  ---             [B]: |----------
```

* __Merge Tracks into One ID__ — Merging tracks is helpful for the same scenario described in "Compare Two Tracks." Say you have an ID named [B] who has most of its track fleshed out. However, at some point it leaves and reenters the frame, labeled as a different ID [A]. Note the following:
  * If both IDs are present on any given frame, then they will each keep their original ID on said frame
  * Unlike swap track, merging modifies tracks across the entire video

_Below are some examples of merging tracks [A] and [B]_

``` bash
BEFORE                             BEFORE                          BEFORE 
[A]:      ---                      [A]: --------  ---              [A]:       ------
[B]: --         ------             [B]:    ----------              [B]: ------

AFTER                              AFTER                           AFTER
[A]:                               [A]:    -----  ---              [A]:         
[B]: --   ---   ------             [B]: -------------              [B]: ------------
```

* __Customize ID Name/Color__ — Convert tracking IDs into real IDs by giving them distinct names and colors. These customizations will be saved for future edits such that the corresponding IDs will not receive default values. Each identity therefore stores the following:
  * Key: int (fixed)
  * Name: String (default = color)
  * Color: String (hex color code or pre-defined color)

* __New ID__ — New ID will create a new unique key that is one more than the greatest existing key. New IDs will initialize with zero bounding boxes, and if left this way, these IDs will not be saved for future edits.

## Committing Edits
**No changes will be saved for future edits if "Commit Edits" is not clicked.** This is essentially a save button for committing edits to a text file in your open directory. Only one text file will be generated and edited per opened video, so clicking the button multiple times will simply update your current working version.

Considering the program currently has no undo button, it is recommended to commit edits frequently to preserve work. For the sake of version control, the original tracking file is left untouched in the main directory, and each editing session is stored chronologically in the "Edited Versions" folder. The program automatically opens the most recent version, so to rid of a session's edits, simply remove the file.

As a safeguard, if the window is closed while there are unsaved changes, the program will automatically create a restored file named "[video-file-name]\_restored\_-1". If this were to occur, upon reopening the video, the user will be prompted to either open the restored file or the most recently saved one. The restored file will be deleted as soon as any edits are committed.

## How to contribute
Go to https://github.com/laurenkafkaloff/Tracklet-Annotator and fork this repository.

Copy the url of your fork and in a terminal on your machine run
```git clone https://github.com/<your_user>/Tracklet-Annotator.git```

Add the upstream repository so that you can pull changes that happen while you are working on your update
```git remote add upstream https://github.com/laurenkafkaloff/Tracklet-Annotator.git```

Make a new local branch. I am calling mine `how-to-contribute`
```git checkout -b <your-branch-name-here>```

Make your updates to the code. You can break down your changes into several sub-tasks that make sense to you. You can type `git status` to show which files have been modified or added.  To add a new file run `git add <filename>` and you will see a new file under "Changes to be committed:". You should continue making changes and "adding" until everything is working for current sub-task you are trying to implement. It is ok if your sub-task update broke something that you plan to fix with a later sub-task, but this step is where you should catch random bugs like off-by-one errors, typos, etc. If your sub-task is ready, you can commit it to the local working branch.

To commit your changes to your local working branch run
```git commit -m "implement zoom function"```

Later, you might have another sub-task to commit
```git commit -m "update box positions to move with zoom"```

After your update is complete, add new GUI tests so we will know if a future change breaks your feature and **go through all existing GUI tests** to make sure your new feature is working and hasn't broken something else. Finally, you can pull any changes that occurred on the upstream main branch into the local version of the upstream main branch, and then "rebase" your new feature branch on those changes (this makes it look like you just did the fork).
```bash
git pull upstream <main/master>
git rebase upstream/<main/master>
```

Push your new branch to the remote version of your/our repo
```git push -u origin <your-branch-name-here>```

Now go online and create a pull request from ```<your-branch-name-here>``` to ```base:<multi-view>```!


