"""
Handles the database
"""
import sqlite3 as sl
import thumbnailgenerator 
import re
import os

class DatabaseHandler(object):
    def __init__ (self):
        self.con = sl.connect('stlDatabase.db')
        self.c = self.con.cursor()
        self.checkTables()

    #if tables not exist create them, mostly needed for the first startup
    def checkTables(self):
       
        self.c.execute('create table if not exists "Items" (itemID INTEGER PRIMARY KEY, name String, path String,hash String,thumbnail String,found INTEGER DEFAULT 0)')
        self.c.execute('create table if not exists "Taggins" (itemID integer, tag String)')
        self.c.execute('create table if not exists "Release" (itemID integer, release String)')
        self.c.execute('create table if not exists "Comments" (itemID integer, comments String)')

    def UpdateItemTable(self, mFileList):
        #compare the hashes of the file list against the hashes of the table
        #hash exists -> check name and folder and change
        #hash does not exist -> create new entry
        #Todo: change so works together with progress bar
        for entry in mFileList:
            with self.con:
                self.c.execute("SELECT * FROM Items WHERE hash = ?",[entry[2]])
                data=self.c.fetchall()
                if len(data)==0:#no data found for that hash, generate entry
                    #generate entry
                    self.c.execute("INSERT INTO Items(name,path,hash,found) VALUES (?,?,?,1)",entry)
                    #get the id 
                    self.c.execute("SELECT * FROM Items WHERE hash = ?",[entry[2]])
                    data=self.c.fetchall()
                    try:
                        print(entry)
                        thumbnailgenerator.createAutoThumb(str(data[0][0]),entry[1])#create thumbnail with filename beeing the itemID of the object, second argument path to stl.
                        path = "Thumbnails/{}.jpg".format(str(data[0][0]))
                    except:
                        path = "Thumbnails/error.jpg"
                    self.c.execute("UPDATE Items SET thumbnail = ? WHERE ItemID = ?",(path,data[0][0]))
                else:# entry exist compare path to see if renamed or moved 
                    if entry[1] != (data[0][2]):#update path 
                        self.c.execute("UPDATE Items SET path = ? , name = ? WHERE itemID =?",(entry[1],entry[0],data[0][0]))
                    #also set found to 1 
                    self.c.execute("UPDATE Items SET found=? WHERE itemID =?",(1,data[0][0]))
        self.cleanUpTables()
    
    def cleanUpTables(self):
        #first clean up taggins table and thumbnail folder
        self.c.execute("SELECT itemID FROM Items WHERE found = 0")
        data=self.c.fetchall()
        for id in data:
            self.c.execute("DELETE FROM Taggins WHERE itemID=?",[id[0]])
            #thumbnail is itemID.jpg
            os.remove("Thumbnails/{}.jpg".format(id[0]))
        # finaly remove entrys that where not found 
        self.c.execute("DELETE FROM Items WHERE found=0")
        #reset found to zero for all entrys
        self.c.execute("UPDATE Items SET found=? WHERE found=?",(0,1))
 
    def getAllFilesThumbnails(self):
    #simply returns all the Thumbnails from the files
        with self.con:
            self.c.execute("SELECT itemID,name,thumbnail FROM Items")
            data=self.c.fetchall()
            returnList = []
            for entry in data:
                returnList.append(entry)
        return returnList

    def searchFilebyName(self,name):
        with self.con:
            self.c.execute("SELECT itemID,name,thumbnail FROM Items WHERE name LIKE ?",[name])
            data = self.c.fetchall()
            returnList = []
            for entry in data:
                returnList.append(entry)
        return returnList

    def searchByTag(self,tag):
        returnList = []
        #get itemID with that tag from taggins
        with self.con:
            self.c.execute("SELECT itemID FROM Taggins WHERE tag =? COLLATE NOCASE",[tag])
            data = self.c.fetchall()
            idList = []
            for entry in data:
                idList.append(entry[0])
        #also search in release (for search purposes handle them just as tags)
            print(tag)
            self.c.execute("SELECT itemID FROM Release WHERE release =? COLLATE NOCASE",[tag])
            data = self.c.fetchall()
            for entry in data:
                idList.append(entry[0])
        #get items by id from items table
        for id in idList:
            result = self.getAllbyID(id)
            returnList.append(tuple(result[0]))
        return tuple(returnList)

    def getPathbyID(self,mID):
        with self.con:
            self.c.execute("SELECT path FROM Items WHERE itemID =?",[mID])
            data = self.c.fetchall()
            returnList = []
            for entry in data:
                returnList.append(entry)
        return returnList   
    
    def getAllbyID(self,mID):
        with self.con:
            self.c.execute("SELECT itemID,name,thumbnail FROM Items WHERE itemID =?",[mID])
            data = self.c.fetchall()
            returnList = []
            for entry in data:
                returnList.append(entry)
        return returnList   

    def getTagsByID(self,mID):
        with self.con:
            self.c.execute("SELECT tag FROM Taggins WHERE itemID =?",[mID])
            data = self.c.fetchall()
            returnList = []
            for entry in data:
                returnList.append(entry[0])
        return returnList
    
    def setTagsByID(self,mID,tagList):
        #delete old tag entrys for this id
        with self.con:
            self.c.execute("DELETE FROM Taggins WHERE itemID =?",[mID])
        for tag in tagList:
            with self.con:
                self.c.execute("INSERT INTO Taggins(itemID,tag) VALUES (?,?)",(mID,tag.strip()))

    def setReleaseByID(self,mID,release):
        #delete old tag entrys for this id
        with self.con:
            self.c.execute("DELETE FROM Release WHERE itemID =?",[mID])
            self.c.execute("INSERT INTO Release(itemID,release) VALUES (?,?)",(mID,release.strip()))

    def getReleaseByID(self,mID):
        with self.con:
            self.c.execute("SELECT release FROM Release WHERE itemID =?",[mID])
            data = self.c.fetchall()
        returnString =""
        for element in data:
            returnString += element[0] + " "
        return returnString
  
    def setCommentsByID(self,mID,comment):
        #delete old tag entrys for this id
        with self.con:
            self.c.execute("DELETE FROM Comments  WHERE itemID =?",[mID])
            self.c.execute("INSERT INTO Comments (itemID,comments) VALUES (?,?)",(mID,comment.strip()))

    def getCommentsByID(self,mID):
        with self.con:
            self.c.execute("SELECT comments FROM Comments WHERE itemID =?",[mID])
            data = self.c.fetchall()
        returnString =""
        for element in data:
            returnString += element[0] + " "
        return returnString

    def getTagNumbers(self):
        #get Tag + how often it is used
        ReturnList = []
        with self.con:
            self.c.execute("SELECT tag FROM Taggins")
            Tags = self.c.fetchall()#list of all tags
            TagsUnique = list(dict.fromkeys(Tags))#remove duplicates by dict
        for entry in TagsUnique:
            amount= Tags.count(entry)
            ReturnList.append([entry[0],amount])
        return sorted(ReturnList, key=lambda tag: tag[1],reverse=True)

    def getItemsWithoutTag(self):
        #return items that have currently no tag 
        with self.con:
            ReturnList = []
            #get all ids in use
            self.c.execute("SELECT itemID FROM Items")
            data = self.c.fetchall()
            #check if id is in taggins if not keep
            for item in data:
                self.c.execute("SELECT itemID FROM taggins WHERE itemID = ?",item)
                data = self.c.fetchall()
                if len(data) == 0 :
                    result = self.getAllbyID(item[0])
                    ReturnList.append(tuple(result[0]))
        return tuple(ReturnList)

class Search(object):
    #handles the translation of the search term into database querys
    def __init__ (self,databasemanager):
        self.databasemanager = databasemanager

    def query(self,term):
        #then returns a list of files
        #terms within [] are tags, terms without extra markings are full text search
        returnList = []
        tagSearchResults = set()
        #find any tag searches in the query 
        tagsToSearch = re.findall(r"\[([ A-Za-z0-9_\-]+)\]", term)
        for tag in tagsToSearch:
            if len(tagSearchResults) == 0:
                tagSearchResults = set(self.databasemanager.searchByTag(tag))
            else:
                tagSearchResults = tagSearchResults.intersection(set(self.databasemanager.searchByTag(tag)))
       

        #remove them from the term
        term = re.sub(r"\[([ A-Za-z0-9_\-]+)\]","",term)
       
        #search with the reminder for filenames           
        fileSearchResults = set(self.databasemanager.searchFilebyName("%{}%".format(term.strip())))
        #print("FileSearchResults: {}".format(fileSearchResults))
        #print("TagSearchResults: {}".format(tagSearchResults))
        if len(tagsToSearch) != 0:
            returnList = fileSearchResults.intersection(tagSearchResults)
        else:
            returnList = fileSearchResults
        return list(returnList)
            


