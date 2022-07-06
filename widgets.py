# -*- coding: utf-8 -*-

try:
    import tkinter as tk
    import tkinter.ttk as ttk
except:
    import Tkinter as tk
    import ttk as ttk

import os
import subprocess
from tracemalloc import start
from turtle import forward
import thumbnailgenerator
import filecrawler
from tkinter import filedialog,messagebox
import json
import math
from PIL import Image, ImageTk
FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')#only works for windows

class Thumbnail(tk.Frame):
    """
    A Frame Holding;
        An Variabel HOlding the itemID
        A Label with the Thumbnail
        A Text Label Under it for the filename
    """
    def __init__(self, parent,itemID, *args, **options):
        i = options.pop('image')
        self.itemID = itemID

        tk.Frame.__init__(self,parent)
        self.mImage = tk.Label(self,image=i)
        self.mImage.grid()

        self.mText = tk.StringVar()
        #TODO: find a way to limit tag size to a fixed size
        self.mName = tk.Label(self,textvariable=self.mText,wraplength=150)
        

        self.mName.grid()

class TagList(tk.Frame):
    #TODO: Add scroolbar
    #a frame holding a list of tags, implemented as a separte widget for easier manipulation
    def __init__(self,parent,root,*args,**options):
        tk.Frame.__init__(self,parent)
        tk.Label(self,text="Tags").grid()
        # add two arrow buttons besides tags for navigating forward and backwarts
        
        self.root = root
        self.NumberOfTags = 1
    
    def clearTags(self):
        self.NumberOfTags = 1
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self,text="Tags").grid()
        

    def setNoTags(self,number):
        noTagLabel = tk.Label(self,text="Items Without Tag: {}".format(number))
        noTagLabel.grid()
        return noTagLabel

    def appendTag(self,tagname,tagnumber):
        self.NumberOfTags +=1
        if self.checkSize() == True:
            mLabel = tk.Label(self,text="{} : ({})".format(tagname,tagnumber))
            mLabel.grid()
            return mLabel
        else:
            return None
 
    def checkSize(self):
        #label is 21px heigh 
        #63px is height of other elements
        #TODO: calculate label height not use pre measurment
        
        self.update()
        self.root.update()
        myHeight = self.winfo_height()
        screenHeight = self.root.winfo_height()

        tagsPerPage = (screenHeight - 63)/21
        print("Tags " + str(self.NumberOfTags) + " of " + str(tagsPerPage) + " Screensize: " + str(screenHeight))
        if self.NumberOfTags > tagsPerPage:
            return False
        else:
            return True
  
class ThumbnailView(ttk.Frame):
    #replacement for the old VerticalScrollFrame
    def __init__(self,parent,*args,**options):
        tk.Frame.__init__(self,parent)
        self.num_elements = 0
        self.max_col = 0
        self.max_row = 0
        self.ThumbsOnPage = 0
        self.currentPage = 1
        self.Pages = 1
        self.thumbList = []
        self.Datatabase = None

        # add navigation bar
        self.butstart = tk.Button(self,text="<<",width=10)
        self.butstart.bind("<Button-1>",self.start)

        self.butbackwards = tk.Button(self,text="<",width=10)
        self.butbackwards.bind("<Button-1>",self.back)
        self.currentPositionText = tk.StringVar()
        self.currentPositionText.set("1")
        self.currentPosition = tk.Entry(self,textvariable=self.currentPositionText,width=10)

        self.maxPositionText = tk.StringVar()
        self.maxPositionText.set("")
        self.maxPosition = tk.Label(self,textvariable=self.maxPositionText,width=10)

        self.butforward = tk.Button(self,text=">",width=10)
        self.butforward.bind("<Button-1>",self.forward)

        self.butend = tk.Button(self,text=">>",width=10)
        self.butend.bind("<Button-1>",self.end)

        self.butstart.grid(row=0,column=0)
        self.butbackwards.grid(row=0,column=1)
        self.currentPosition.grid(row=0,column=2)
        self.maxPosition.grid(row=0,column=3)
        self.butforward.grid(row=0,column=4)
        self.butend.grid(row=0,column=5)

    def setFiles(self,files):
        self.files = files    
        self.displayThumbnails()

    def setDatabase(self,database):
        self.Datatabase = database
    def displayThumbnails(self):
        #clear thumbnails
        for item in self.thumbList:
            item.destroy()
        self.thumbList =[]
      
        self.calculateRowsAndColumns()

        self.Pages = math.ceil(len(self.files)/self.ThumbsOnPage)
        self.maxPositionText.set(self.Pages)

        n = 0 
        row_num = 1
        col_num = 0

        while n < self.ThumbsOnPage:
            if n + (self.ThumbsOnPage * (self.currentPage -1)) >= len(self.files):
                break
            if col_num == self.max_col:
                col_num = 0
                row_num +=1

            image = Image.open(self.files[n + (self.ThumbsOnPage * (self.currentPage -1))][2])
            image = image.resize((150, 150), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image)
            l = Thumbnail(self,self.files[n + (self.ThumbsOnPage * (self.currentPage -1))][0],image=photo)
            l.mImage.image = photo#reference keeping
            l.mText.set(self.files[n + (self.ThumbsOnPage * (self.currentPage -1))][1])
            l.grid(row = row_num,column=col_num,sticky=tk.N+tk.S)
            l.mImage.bind("<Button-1>",self.callbackLabel)
            l.mName.bind("<Button-1>",self.callbackLabel)

            self.thumbList.append(l)
            col_num +=1
            n +=1
        

    def calculateRowsAndColumns(self):
        #based on frame size calculate the number of thumbs to display
        self.max_col = math.floor(self.winfo_width()/150)
        self.max_row = math.floor(self.winfo_height()/(150 +75))
        self.ThumbsOnPage = self.max_col * self.max_row
        #avoid division by zero
        if self.ThumbsOnPage == 0:
            self.ThumbsOnPage = 1

    def set_NumberOfElements(self,number):
        self.num_elements = int(number)

    def get_NumberOfElements(self):
        return self.num_elements
   
    def start(self,event):
        self.currentPage = 1
        self.currentPositionText.set(self.currentPage)
        self.displayThumbnails()

    def back(self,event):
        if self.currentPage > 1:
            self.currentPage -= 1
            self.currentPositionText.set(self.currentPage)
            self.displayThumbnails()

    def forward(self,event):
        if self.currentPage < self.Pages:
            self.currentPage += 1
            self.currentPositionText.set(self.currentPage)
            self.displayThumbnails()

    def end(self,event):
        self.currentPage = self.Pages
        self.currentPositionText.set(self.currentPage)
        self.displayThumbnails()

    def callbackLabel(self,event):
        MyDialog(self,self.Datatabase,event.widget.master.itemID,event.widget.master)#also pass the itemID to the dialog
        
class Dialog(tk.Toplevel):
    #a base class for dialog windows
    # https://effbot.org/tkinterbook/tkinter-dialog-windows.htm
    def __init__(self, parent,title = None):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body =tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = tk.Frame(self)

        w = tk.Button(box, text="Apply", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        #todo: readd the chancel button
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.apply()
        self.withdraw()
        self.update_idletasks()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1 # override

    def apply(self):

        pass # override

class MyDialog(Dialog):

    def __init__(self,parent,databaseHandler,itemID,widget,title= None):
        self.itemID = itemID
        self.databaseHandler  = databaseHandler
        self.widget = widget
        Dialog.__init__(self,parent,title=title)

    def body(self,master):
        self.mButtonExplorer = tk.Button(master,text="Reveale in File Explorer",command=self.showExplorer).grid(row=0)
        self.mButtonThumb = tk.Button(master,text="Edit Thumbnail",command=self.editThumbnail).grid(row=1)
        #Tag list
        tk.Label(master,text="Tags (Seperated by ,):").grid(row=2)
        self.mTags = tk.Text(master,height=3,width=75)
        self.mTags.grid(row=3)
        #construct tag text
        mTagsText = ""
        for entry in self.databaseHandler.getTagsByID(self.itemID):
            mTagsText += entry + ","
        mTagsText = mTagsText.rstrip(",")
        self.mTags.insert(1.0,mTagsText)
        
        #Release Field
        tk.Label(master,text="Release:").grid(row=4)
        self.mRelease = tk.Text(master,height=1,width=75)
        self.mRelease.grid(row=5)
        releaseText = self.databaseHandler.getReleaseByID(self.itemID)
        self.mRelease.insert(1.0,releaseText)
        
        #Comments
        tk.Label(master,text="Comments:").grid(row=6)
        self.mComments = tk.Text(master,height=3,width=75)
        self.mComments.grid(row=7)
        commentsText = self.databaseHandler.getCommentsByID(self.itemID)
        self.mComments.insert(1.0,commentsText)
        
    def apply(self):
        text = self.mTags.get("1.0",tk.END)
        tagList = text.split(",")
        self.databaseHandler.setTagsByID(self.itemID,tagList)

        release = self.mRelease.get("1.0",tk.END)
        self.databaseHandler.setReleaseByID(self.itemID,release)

        comment = self.mComments.get("1.0",tk.END)
        self.databaseHandler.setCommentsByID(self.itemID,comment)
        #TODO: update sidebar!        

    def showExplorer(self):
        path = self.databaseHandler.getPathbyID(self.itemID)[0]
        path =  path[0]
        subprocess.run([FILEBROWSER_PATH, '/select,', os.path.normpath(path)]) #only works for windows!
    
    def editThumbnail(self):
        thumbnailgenerator.createManualThumb(self.itemID,self.databaseHandler.getPathbyID(self.itemID)[0][0],self.widget)

class SettingsDialog(Dialog):

    def __init__(self,parent,config):
        self.config = config
        self.CrawlVar = tk.IntVar()
        self.directory =""
        self.oldFolder = self.config["Folder"]
        self.Button = None
        Dialog.__init__(self,parent,title="Settings")

    def body(self,master):
        #checkbox for crawling on startup or not
        self.CrawlVar  = tk.IntVar()
        if self.config["CrawlOnStartup"] == "True":
            self.CrawlVar.set(1)
        else:
            self.CrawlVar.set(0)

        c = tk.Checkbutton(master, text="Crawl on Startup", variable=self.CrawlVar)
        c.grid()
        #number of tags    
        tk.Label(master,text="Number of Tags to Display in Sidebar:").grid(row=1,column=0)
        self.NumberOfTags = tk.Entry(master)
        self.NumberOfTags.grid(row=1,column=1)

        #folder to crawl
        self.directory = self.config["Folder"]
        tk.Label(master,text="Folder to Crawl:").grid(row=2,column=0)
        self.Button = tk.Button(master,text=self.directory,command=self.selectFile)
        self.Button.grid(row=2,column=1)

    def selectFile(self):
        self.directory = filedialog.askdirectory()
        self.Button.configure(text=self.directory)

    def apply(self):
        if self.CrawlVar.get() == 1:
            self.config["CrawlOnStartup"] = "True"
        else:
            self.config["CrawlOnStartup"] = "False"
        if self.config["Folder"] != "" and self.config["Folder"] != self.oldFolder:#warning if folder changed from no folder
            messagebox.showinfo("Folder Changed","Folder Changed, consider making a backup of stlDatabase.db\nFiles not found during the next crawl will be removed from the database") 
        self.config["Folder"] = self.directory
        #save config changes to file
        with open('settings.json', 'w') as outfile:
            json.dump(self.config, outfile)

class CrawlingDialog(Dialog):
    
    def __init__(self,parent,config,databasehandler):
        self.config = config
        self.mDatabaseHandler = databasehandler
        self.progressbar = None
        self.mFileCrawler = filecrawler.FileCrawler(self.config["Folder"])
        Dialog.__init__(self,parent,title="Crawling")

    def body(self,master):
        tk.Label(master,text="Crawling Folder: {} containing {} Files.\nThis may take a while\nPress apply to Start".format(self.config["Folder"],filecrawler.getFileNumber(self.config["Folder"]))).grid()          
        self.progressbar= tk.ttk.Progressbar(master,orient="horizontal",length=300,mode="determinate")
        self.progressbar.grid()
        self.progressbar["value"]=0
        self.progressbar["maximum"]=filecrawler.getFileNumber(self.config["Folder"])

    def apply(self):
        mFileList = self.mFileCrawler.crawl(self.progressbar)
        #todo: add an info that crawling is done, database  gets updated now
        self.mDatabaseHandler.UpdateItemTable(mFileList)


