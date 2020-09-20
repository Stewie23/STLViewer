# -*- coding: utf-8 -*-

try:
    import tkinter as tk
    import tkinter.ttk as ttk
except:
    import Tkinter as tk
    import ttk as ttk

import os
import subprocess
import thumbnailgenerator
from tkinter import filedialog,messagebox
import json
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
        self.mName = tk.Label(self,textvariable=self.mText,wraplength=150)
        

        self.mName.grid()

class VerticalScrollFrame(ttk.Frame):
    """A ttk frame allowing vertical scrolling only.
    Use the '.interior' attribute to place widgets inside the scrollable frame.
    Adapted from https://gist.github.com/EugeneBakin/76c8f9bcec5b390e45df.
    Amendments:
    1. Original logic for configuring the interior frame and canvas
       scrollregion left canvas regions exposed (not suppose to) and allowed
       vertical scrolling even when canvas height is greater than the canvas
       required height, respectively. I have provided a new logic to
       resolve these issues.
    2. Provided options to configure the styles of the ttk widgets.
    3. Tested in Python 3.5.2 (default, Nov 23 2017, 16:37:01),
                 Python 2.7.12 (default, Dec  4 2017, 14:50:18) and
                 [GCC 5.4.0 20160609] on linux.
    Author: Sunbear
    Website: https://github.com/sunbearc22
    Created on: 2018-02-26
    Amended on: 2018-03-01 - corrected __configure_canvas_interiorframe() logic.  
    """

    
    def __init__(self, parent, *args, **options):
        """
        WIDGET-SPECIFIC OPTIONS:
           style, pri_background, sec_background, arrowcolor,
           mainborderwidth, interiorborderwidth, mainrelief, interiorrelief 
        """
        # Extract key and value from **options using Python3 "pop" function:
        #   pop(key[, default])
        style          = options.pop('style',ttk.Style())
        pri_background = options.pop('pri_background','light grey')
        sec_background = options.pop('sec_background','grey70')
        arrowcolor     = options.pop('arrowcolor','black')
        mainborderwidth     = options.pop('mainborderwidth', 0)
        interiorborderwidth = options.pop('interiorborderwidth', 0)
        mainrelief          = options.pop('mainrelief', 'flat')
        interiorrelief      = options.pop('interiorrelief', 'flat')

        ttk.Frame.__init__(self, parent, style='main.TFrame',
                           borderwidth=mainborderwidth, relief=mainrelief)

        self.__setStyle(style, pri_background, sec_background, arrowcolor)

        self.__createWidgets(mainborderwidth, interiorborderwidth,
                             mainrelief, interiorrelief,
                             pri_background)
        self.__setBindings()


    def __setStyle(self, style, pri_background, sec_background, arrowcolor):
        '''Setup stylenames of outer frame, interior frame and verticle
           scrollbar'''        
        style.configure('main.TFrame', background=pri_background)
        style.configure('interior.TFrame', background=pri_background)
        style.configure('canvas.Vertical.TScrollbar', background=pri_background,
                        troughcolor=sec_background, arrowcolor=arrowcolor)

        style.map('canvas.Vertical.TScrollbar',
            background=[('active',pri_background),('!active',pri_background)],
            arrowcolor=[('active',arrowcolor),('!active',arrowcolor)])


    def __createWidgets(self, mainborderwidth, interiorborderwidth,
                        mainrelief, interiorrelief, pri_background):
        '''Create widgets of the scroll frame.'''
        self.vscrollbar = ttk.Scrollbar(self, orient='vertical',
                                        style='canvas.Vertical.TScrollbar')
        self.vscrollbar.pack(side='right', fill='y', expand='false')
        self.canvas = tk.Canvas(self,
                                bd=0, #no border
                                highlightthickness=0, #no focus highlight
                                yscrollcommand=self.vscrollbar.set,#use self.vscrollbar
                                background=pri_background #improves resizing appearance
                                )
        self.canvas.pack(side='left', fill='both', expand='true')
        self.vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = ttk.Frame(self.canvas,
                                  style='interior.TFrame',
                                  borderwidth=interiorborderwidth,
                                  relief=interiorrelief)
        self.interior_id = self.canvas.create_window(0, 0,
                                                     window=self.interior,
                                                     anchor='nw')


    def __setBindings(self):
        '''Activate binding to configure scroll frame widgets.'''
        self.canvas.bind('<Configure>',self.__configure_canvas_interiorframe)
        

    def __configure_canvas_interiorframe(self, event):
        '''Configure the interior frame size and the canvas scrollregion'''
        #Force the update of .winfo_width() and winfo_height()
        self.canvas.update_idletasks() 

        #Internal parameters 
        interiorReqHeight= self.interior.winfo_reqheight()
        canvasWidth    = self.canvas.winfo_width()
        canvasHeight   = self.canvas.winfo_height()

        #Set interior frame width to canvas current width
        self.canvas.itemconfigure(self.interior_id, width=canvasWidth)
        
        # Set interior frame height and canvas scrollregion
        if canvasHeight > interiorReqHeight:
            #print('canvasHeight > interiorReqHeight')
            self.canvas.itemconfigure(self.interior_id,  height=canvasHeight)
            self.canvas.config(scrollregion="0 0 {0} {1}".
                               format(canvasWidth, canvasHeight))
        else:
            #print('canvasHeight <= interiorReqHeight')
            self.canvas.itemconfigure(self.interior_id, height=interiorReqHeight)
            self.canvas.config(scrollregion="0 0 {0} {1}".
                               format(canvasWidth, interiorReqHeight))

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

        self.withdraw()
        self.update_idletasks()

        self.apply()

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
        tk.Label(master,text="Tags (Seperated by ,):").grid(row=2)
        self.mTags = tk.Text(master,height=3,width=75)
        self.mTags.grid(row=3)
        #construct tag text
        mTagsText = ""
        for entry in self.databaseHandler.getTagsByID(self.itemID):
            mTagsText += entry + ","
        mTagsText = mTagsText.rstrip(",")
        self.mTags.insert(1.0,mTagsText)


    def apply(self):
        text = self.mTags.get("1.0",tk.END)
        tagList = text.split(",")
        self.databaseHandler.setTagsByID(self.itemID,tagList)


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
        #folder to crawl
        self.directory = self.config["Folder"]
        tk.Label(master,text="Folder to Crawl:").grid(row=1,column=0)
        self.Button = tk.Button(master,text=self.directory,command=self.selectFile)
        self.Button.grid(row=1,column=1)

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

        
