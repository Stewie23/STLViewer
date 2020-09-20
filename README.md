# STLViewer
Shows STL Files from a Folder with Preview Pictures (using VTK), and points to them in the Explorer.
Probably just works with Windows for now.

**Features:**

* Finds all .stl Files within a folder and all its subfolders and stores their hashes, files can be moved or renamed and still will be found.
Deleted or edited files, as editing would change their hash,will be removed from the database

* Points to the Files in the Windows Explorer

* Automaticaly Generates a Preview Picture, since this will often be from a wierd angle, the picture can be manualy edited. 

* Allows to asign Tags to Files

* Search for Tags via  []

* Search within filenames

**some features are missing:**

* changing the folder that is crawled

* manual crawling, crawling at startup

**planned features:**

* more refined searchfeatures

* Hash changed but filename is known, dialog if new file should get the old tags
