#!/usr/bin/python3
"""
Savestat.py

A class to save a varable or array in a file

To limit writes the content to store is buffered after write.
On the next save ist's compared with the buffer and only written
when content has changed

Usage:
from Savestat import Savestat
save1 = Savestat(fullFilename)
save1.set(var-array)
var-array = save1.get()
print('status : ',save1.get_stat())

Author Johann Maurer 

Version 1.1   2020-07-25
-   better debug info
-   better status info
Version 1.0   2020-07-22

ToDo
- Destructor to remove 
"""

import sys
import json
import os
import time

class Savestat:
    def __init__(self,fullFilename,debug=False):
        """
        save = Savestat(fullFilename,debug) 
        - fullFilename example "/home/xxx/tstat.json'
        - debug = true or False
        """
        self.fname = fullFilename
        self.content = False
        self.time = 0
        self.debug = debug
        self.status = 'run'
        try:
            fstat = os.stat(self.fname).st_mtime
            self.time = fstat
        except:
            self.status = 'No data'
        if self.debug: 
            print("file: {} status: {} stime {:010.0f}".format(self.fname, self.status, self.time))

    def get_stat(self):
        """
        Return the status of the local buffer
        """     
        if self.debug: 
            print("file: {} status: {} stime {:010.0f}".format(self.fname,self.status,self.time))
        return self.status

    def get(self) :
        """
        Return the the actual content
        """
        try :
            lastmod = os.stat(self.fname).st_mtime
        except :
            return False
        if lastmod > self.time or not self.content: 
            cf = open(self.fname,'r')
            self.content = cf.read()
            cf.close()
            self.time = lastmod
            self.status = 'read'
        else :
            self.content = self.content
            self.status = 'buffer'
        if self.debug : 
            print("file: {} status: {} stime {:010.0f} data: {}".format(self.fname,self.status,self.time,self.content))
        return json.loads(self.content)

    def set(self,content) :
        """
        Save content (var or array) as a json string
        to the file defined. The file is only written
        when the content is not equal the local buffer 
        """
        newcontent = json.dumps(content)
        if self.content == newcontent:
            # no difference 
            self.status = 'skip'
        else:
            # Different data -> save to file
            cf = open(self.fname,'w')
            cf.write(newcontent)
            cf.close()
            self.content = newcontent
            self.time = time.time()
            self.status = 'write'
        if self.debug: 
            print("file: {} status: {} stime {:010.0f} data: {}".format(self.fname,self.status,self.time,self.content))
        return True
# end class Savestat

