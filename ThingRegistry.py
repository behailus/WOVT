'''
  Copyright (c) 2017, Behailu S. Negash.
  All rights reserved.
 
  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions
  are met:
  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
  3. Neither the name of the Institute nor the names of its contributors
     may be used to endorse or promote products derived from this software
     without specific prior written permission.
 
  THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
  ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
  OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
  OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
  SUCH DAMAGE.
 
  This file is part of the Web of Virtual Things.
 
  Author: Behailu S. Negash <behneg@utu.fi>
  
'''
from Configurations import RegistryConfig
from ThingAttribute import ThingAttribute
import threading 
import queue
import time
import logging
import json
#This is a singleton class as it has to be the only instance running 
class Registry:
    class _registry:
        def __init__(self):            
            self.Store = {}
            
        def ThingAlive(self, objId):
            if objId in self.Store:
                return True
            else:
                return False
        
        def Register(self, obj, observer):
            if(len(self.Store) < RegistryConfig.RegistrySize):
                self.Store[obj.mdata.uid] = obj
                logging.debug("Registered "+obj.mdata.uid)
                observer(obj)
                return 1
            else:
                return 0

        def Update(self, objId):
            thing = self.Store[objId]
            thing.mdata.LastUpdate = int(round(time.time()*1000)) #in ms
            self.Store[objId] = thing
            logging.debug("Updated: "+thing.toJson())
            
        
        def Modify(self, obj, vals, observer=None):
            prps = json.loads(vals)
            self.Store[obj].attrs = ThingAttribute(**prps)
            '''for key in prps:
                self.Store[obj].addAttr(key, prps.get(key))'''
            logging.debug("Object modified")
            if observer != None:
                observer(self.Store[obj])

        def GarbageCollector(self, observer):
            for key in self.Store:
                item = self.Store[key]
                if (int(round(time.time()*1000)) - item.mdata.LastUpdate) > item.mdata.activeTime*1000:#there is a 1000 factor
                    logging.debug("Removing item: "+item.mdata.uid)
                    del self.Store[item.mdata.uid]
                    observer(key)
                    return item
            
             

    Instance = None
    def __init__(self):
        if not Registry.Instance:
            Registry.Instance = Registry._registry()



