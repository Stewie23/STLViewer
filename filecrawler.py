# -*- coding: utf-8 -*-

import pathlib
import hashlib
import os

"""
goes trough a folder and looks for .stl files, put them into a list 
returns a nestet list containing name,folder and hash
"""
class FileCrawler(object):
    def __init__ (self,folder):
        self.folder = folder 
        self.MySTLList = []

    
    def crawl(self):
        doubleLog = open("doublefiles.txt","w")
        listOfFiles = list(pathlib.Path(self.folder).glob('**/*.stl'))
        for file in listOfFiles:
            filename = os.path.basename(file).split(".")[0]#os.path.basename only works for windows apperantly
            with open(file, "rb") as f:
                file_hash = hashlib.blake2b()
                while chunk := f.read(8192):
                    file_hash.update(chunk)
            entry = [filename,str(file),file_hash.hexdigest()]

            if self.checkDouble(entry[2]) == False: #no duplication
                self.MySTLList.append(entry)
            else:
                doubleLog.write("Ignoring Duplicated File: {} \n".format(entry[1]))
        doubleLog.close()
        return self.MySTLList

    def checkDouble(self,hash):
        if len(self.MySTLList) > 0:
            for entry in self.MySTLList:
                if entry[2] == hash:
                    return True
            return False
        else:
            return False
