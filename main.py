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

class App:

    def __init__(self,root):
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
        self.left_frame = widgets.VerticalScrollFrame(root)
        self.left_frame.grid(row=1,sticky='nsew')
        #self.setupThumbnails(self.left_frame)
        #right frame for displaying tags, and additionial info
        self.right_frame = tk.Frame(root)
        self.right_frame.grid(row=1,column=1,sticky="nw")
        #display # of search results
        self.resultNumLable = tk.Label(self.right_frame, text="Results:")
        self.resultNumLable.grid()
        #tag widget
        self.TagWidget = widgets.TagList(self.right_frame)
        self.TagWidget.grid()
        #search variable
        
        #after setting up the basic gui. crawl and set up the database
        #init database
        #print("Initialising Database..")
        self.mDatabaseHandler = databasehandler.DatabaseHandler()
        self.Search = databasehandler.Search(self.mDatabaseHandler)
        if self.config["CrawlOnStartup"] == "True":
            Crawl()         
        else:
            #passing the inital list of files to the thumbnails
            self.setupThumbnails(self.mDatabaseHandler.getAllFilesThumbnails())

        self.updateSidebar()
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
        #reset first
        for item in self.left_frame.interior.winfo_children():
            item.destroy()
        #populating
        rn = 0
        cn = 0
        #update result label
        self.resultNumLable.config(text="Results: {}".format(len(listOfFiles)))
        #build the actual thumbnails
        for mFile in listOfFiles:
            if cn == self.columnumber-1:
                cn = 0
                rn +=1
            image = Image.open(mFile[2])
            image = image.resize((150, 150), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image)
            l = widgets.Thumbnail(self.left_frame.interior,mFile[0],image=photo)
            l.mImage.image = photo#reference keeping
            l.mText.set(mFile[1])
            l.grid(row = rn,column=cn,sticky=tk.N+tk.S)
            l.mImage.bind("<Button-1>",self.callbackLabel)
            l.mName.bind("<Button-1>",self.callbackLabel)
            cn += 1

    def updateSidebar(self):
        self.TagWidget.clearTags()
        #updating the list of tags and their numbers
        tags = self.mDatabaseHandler.getTagNumbers()
        noTagLable = self.TagWidget.setNoTags(len(self.mDatabaseHandler.getItemsWithoutTag()))
        noTagLable.bind("<Button-1>",self.NoTagSearch)
        for entry in tags:
            Label = self.TagWidget.appendTag(entry[0],entry[1])
            Label.bind("<Button-1>",self.doSearch)

    def callbackLabel(self,event):
        widgets.MyDialog(self.root,self.mDatabaseHandler,event.widget.master.itemID,event.widget.master)#also pass the itemID to the dialog
        self.updateSidebar()
 
    def resizeEvent(self,event):
        #based on the width, determin how many thumbnails are displayed in a row
        #a thumbnail beeing 150X150px,havging a 4px of border (in total) 
        #-200 for the tag display
        columnnumber = math.trunc((self.root.winfo_width()-200)/154)
        if self.columnumber != columnnumber:
            self.columnumber = columnnumber
            #redraw thumbs
            rn = 0
            cn = 0
            for widget in self.left_frame.interior.winfo_children():
                if cn == self.columnumber:
                    cn = 0
                    rn +=1
                widget.grid(row=rn,column=cn)
                cn+=1

root = tk.Tk()
root.title("STL Viewer")
app = App(root)
root.mainloop()
