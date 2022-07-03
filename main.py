import tkinter as tk
from tkinter import messagebox
import pathlib
from PIL import Image, ImageTk
import widgets
import math
import filecrawler
import databasehandler
import os
import json
import vtkmodules.all

class App:

    def __init__(self,root):
        self.oldHeight = 800
        self.go = False
        def SettingsDialog():
             widgets.SettingsDialog(self.root,self.config)#also pass the itemID to the dialog
            
        def Crawl():
            #crawl the file system if theres a folder defined
            if self.config["Folder"] != "":
                widgets.CrawlingDialog(self.root,self.config,self.mDatabaseHandler)
                self.setupThumbnails(self.mDatabaseHandler.getAllFilesThumbnails())
            else:
                messagebox.showinfo("No Folder to crawl", "Please define a Folder in the Settings before Crawling")
        self.config = ""
        self.checkConfig()
        frame = tk.Frame(root)
        self.root = root
        self.root.minsize(300,300)
        self.root.geometry("800x800")
        
        self.columnumber = 0 
        self.root.bind("<Configure>" ,self.resizeEvent)
        frame.grid()
        self.searchvariable = tk.StringVar()
        # create a toplevel menu
        menubar = tk.Menu(root)
        menubar.add_command(label="Settings", command=SettingsDialog)
        menubar.add_command(label="Crawl",command=Crawl)
        root.config(menu=menubar)
        #creating frames for handling the layout (top,left,right)
        top_frame = tk.Frame(root) 
        top_frame.grid(row=0,sticky="we")  
        root.columnconfigure(0,weight=1)
        root.columnconfigure(1,weight=0,minsize=200)
        root.rowconfigure(1,weight=1)
        self.setupSearchbar(top_frame)
        #the thumnail frame
        #self.left_frame = widgets.VerticalScrollFrame(root)
        self.left_frame = widgets.ThumbnailView(root)
        self.left_frame.grid(row=1,sticky='nsew')
        #self.setupThumbnails(self.left_frame)
        #right frame for displaying tags, and additionial info
        self.right_frame = tk.Frame(root)
        self.right_frame.grid(row=1,column=1,sticky="nw")
        #display # of search results
        self.resultNumLable = tk.Label(self.right_frame, text="Results:")
        self.resultNumLable.grid()
        #tag widget
        self.TagWidget = widgets.TagList(self.right_frame,self.root)
        self.TagWidget.grid()
        
        #search variable
        
        #after setting up the basic gui. crawl and set up the database
        #init database
        print("Initialising Database...")
        self.mDatabaseHandler = databasehandler.DatabaseHandler()
        self.Search = databasehandler.Search(self.mDatabaseHandler)
        self.left_frame.setDatabase(self.mDatabaseHandler)
        print("... done")
        if self.config["CrawlOnStartup"] == "True":
            Crawl()         
        else:
            #passing the inital list of files to the thumbnails
            print("setup Thumbnails ...")
            #TODO: comment so it starts for now
            self.setupThumbnails(self.mDatabaseHandler.getAllFilesThumbnails()) 
            print("... done")
        print ("update Sidebar")    
        self.updateSidebar()
        print ("... done")
        self.go = True

    def checkConfig(self):
        #look for a config file, if exist use it if not generate and set flag for settings dialog
        if os.path.isfile("settings.json") == True:
            #use settings
            self.config = json.load(open("settings.json", "r"))
        else:
            #generate empty and load
            f = open("settings.json", "a")
            f.write("{\n \"Folder\":\"\",\n\"CrawlOnStartup\":\"False\"\n}")
            f.close()
            self.config = json.load(open("settings.json", "r"))

    def setupSearchbar(self,frame):
        #creating the searchbar 
        searchbar = tk.Entry(frame,textvariable=self.searchvariable,width=100)
        searchbar.grid(row=0)
        searchbar.bind("<Key>",lambda event,a=self.searchvariable,b=searchbar: self.sendSearchString(event,a,b))
        self.searchvariable.set("Search")
        searchbar = self.searchvariable.get()

    def sendSearchString(self,event,stringVar,entry):
        if event.keysym == "Return":#user hit return get searching
            returnList = self.Search.query(entry.get())
            self.setupThumbnails(returnList)

    def doSearch(self,event):
        query = event.widget.cget("text") 
        #remove number and strip
        query = query.split(":")[0]
        query = query.strip()
        #do a search thats not happend via the searchbar 
        returnList = self.Search.query("["+query+"]")   
        self.setupThumbnails(returnList)
        #also set the searchbar text to reflext the search
        self.searchvariable.set("["+query+"]")

    def NoTagSearch(self,event):
        returnList = self.mDatabaseHandler.getItemsWithoutTag()
        self.setupThumbnails(returnList)
        self.searchvariable.set("[NoTag]")

    def setupThumbnails(self,listOfFiles):
        #TODO: at some number of preview picuteres displaying them fails - should probably change this code to only load one page worth of preview pictures
        self.left_frame.setFiles(listOfFiles)

    def updateSidebar(self):
        self.TagWidget.clearTags()
        #updating the list of tags and their numbers
        tags = self.mDatabaseHandler.getTagNumbers()
        noTagLable = self.TagWidget.setNoTags(len(self.mDatabaseHandler.getItemsWithoutTag()))
        noTagLable.bind("<Button-1>",self.NoTagSearch)
        for entry in tags:
            Label = self.TagWidget.appendTag(entry[0],entry[1])
            Label.bind("<Button-1>",self.doSearch)

    def resizeEvent(self,event):
        self.left_frame.calculateRowsAndColumns()
        pass



root = tk.Tk()
root.title("STL Viewer")
app = App(root)
root.mainloop()
