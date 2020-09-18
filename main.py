import tkinter as tk
import pathlib
from PIL import Image, ImageTk
import widgets
import math
import filecrawler
import databasehandler
class App:

    def __init__(self,root):
        frame = tk.Frame(root)
        self.root = root
        self.root.minsize(300,300)
        self.root.geometry("800x800")
        self.columnumber = 0 
        self.root.bind("<Configure>" ,self.resizeEvent)
        frame.grid()

        # create a toplevel menu
        menubar = tk.Menu(root)
        menubar.add_command(label="Dummy!")
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
        right_frame = tk.Frame(root)
        right_frame.grid(row=1,column=1,sticky="nw")
        #display # of search results
        self.resultNumLable = tk.Label(right_frame, text="Results:")
        self.resultNumLable.grid()
        w = tk.Label(right_frame, text="Tags")
        w.grid()

        #after setting up the basic gui. crawl and set up the database
        #init database
        print("Initialising Database..")
        self.mDatabaseHandler = databasehandler.DatabaseHandler()
        self.Search = databasehandler.Search(self.mDatabaseHandler)
        #crawl the file sstem
        #print("Crawling Filesystem ... this may take a while")
        #mFileCrawler = filecrawler.FileCrawler("F:/3DPrinting")
        #mFileList = mFileCrawler.crawl()
        #print("Done Crawling Filesystem")        
        #feed the file list into the database
        #print("Updating Database")
        #self.mDatabaseHandler.UpdateItemTable(mFileList)
        #passing the inital list of files to the thumbnails
        self.setupThumbnails(self.mDatabaseHandler.getAllFilesThumbnails())


    def setupSearchbar(self,frame):
    #creating the searchbar
        v = tk.StringVar()
        searchbar = tk.Entry(frame,textvariable=v,width=100)
        searchbar.grid(row=0)
        searchbar.bind("<Key>",lambda event,a=v,b=searchbar: self.sendSearchString(event,a,b))
        v.set("Search")
        searchbar = v.get()


    def sendSearchString(self,event,stringVar,entry):
        if event.keysym == "Return":#user hit return get searching
            returnList = self.Search.query(entry.get())
            self.setupThumbnails(returnList)
        

    def setupThumbnails(self,listOfFiles):
        #reset first
        for item in self.left_frame.interior.winfo_children():
            item.destroy()
        #populating
        rn = 0
        cn = 0
        #update result label
        self.resultNumLable.config(text="Results: {}".format(len(listOfFiles)))
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

    def callbackLabel(self,event):
        widgets.MyDialog(self.root,self.mDatabaseHandler,event.widget.master.itemID)#also pass the itemID to the dialog

  
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
