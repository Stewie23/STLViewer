# STLViewer
Shows STL Files from a Folder with Preview Pictures (using VTK), and points to them in the Explorer.
Probably just works with Windows for now.

The Thumbnail editing is not documented at all, once the thumbnail shows manipulate its orientation with the mouse. Pressing the Enter key will make a new screenshot, to see your changes close the Thumbnail window. Dont try to manipulate other windows while the Thumbnail editing window is open.

**Features:**

* Finds all .stl Files within a folder and all its subfolders and stores their hashes, files can be moved or renamed and still will be found.
Deleted or edited files, as editing would change their hash,will be removed from the database

* Points to the Files in the Windows Explorer

* Automaticaly Generates a Preview Picture, since this will often be from a wierd angle, the picture can be manualy edited. 

* Allows to asign mutiple Tags to Files. Files also can have a Release and Comments assigend to them.

* Search for Tags/Releases via  []

* Search within filenames

**planned features:**

* more refined searchfeatures

* Hash changed but filename is known, dialog if new file should get the old tags

**Known Problems:**

* Having a manual Thumbwindow open and manipulating the Dialogmenu does not work well
