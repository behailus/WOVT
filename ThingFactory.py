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
  

This is the factory class that generates the 'Thing' agents with all the behaviours, events and properties that is defined in the data model. 

This will have multiple implementations for different data models: OCF, IPSO, W3C or any other
'''

import ThingBase
from ThingAttribute import ThingAttribute,Thing
from Utils import Parser
import logging
from Configurations import Config
import time
class ThingFactory:
    factories = {}
    parser = None
    class W3CFactory:
        def __init__(self):
            pass 

        @staticmethod
        def CreateThing(url, ninterface):
            met={}
            met['uid'] = url
            met['netif'] = ninterface
            met['LastUpdate'] = int(round(time.time()*1000)) #in ms
            url = Config.W3CModelRoot+url
            ThingFactory.parser = Parser(url,'JSON')
            thng = ThingFactory.parser.Parse()
            logging.debug('Parsed W3C thing from '+url)
            #Now create the thing 
            met['context'] = thng['@context']
            #Metadata
            for key in thng:
                if not (type(thng[key]) == dict or type(thng[key])==list):
                    met[key] = thng[key]
            #properties
            pro = {}
            try:
                prop = thng['interactions']
                for p in prop:
                    if p['@type'][0]=='Property':
                        pro[p['name']]=None
            except KeyError:
                pro = {}
            meta = ThingAttribute(**met)
            props = ThingAttribute(**pro)
            actns = ThingAttribute(**pro)
            thing = Thing(meta,props,actns)
            return thing

    class OCFFactory:
        def __init__(self):
            pass
        @staticmethod
        def CreateThing(url, ninterface):
            met = {}
            met['uid'] = url
            met['netif'] = ninterface
            met['LastUpdate'] = int(round(time.time()*1000)) #in ms
            url = Config.OCFModelRoot+url
            ThingFactory.parser = Parser(url,'JSON')
            thng = ThingFactory.parser.Parse()
            logging.debug('Parsed OCF thing from '+url)
            #Now create the thing
            met['schema'] = thng['$schema']
            #Metadata
            for key in thng:
                if not (type(thng[key]) == dict or type(thng[key])==list):
                        met[key] = thng[key]
            #properties
            pro = {}
            try:
                prop = thng['definitions']
                for p in prop:
                    ppts = prop[p]['properties']
                    for pp in ppts:
                        pro[pp] = None
            except KeyError:
                pro = {}             
            
            meta = ThingAttribute(**met)
            props = ThingAttribute(**pro)
            actns = ThingAttribute(**pro)
            thing = Thing(meta,props,actns)
            return thing

    class IPSOFactory:
        def __init__(self):
            pass
        @staticmethod
        def CreateThing(url, ninterface):           
            met = {}
            met['uid'] = url
            met['netif'] = ninterface
            met['LastUpdate'] = int(round(time.time()*1000)) #in ms
            url = Config.IPSOModelRoot+url
            ThingFactory.parser = Parser(url,'XML')
            thng = ThingFactory.parser.Parse()
            logging.debug('Parsed IPSO thing from '+url)
            #Now create the thing  
            root = thng.getroot() 
            #Metadata
            res = root.find('Object')
            name = res.find('Name')
            met['Name'] = name.text
            met['schema'] = str(root.attrib)
            
            #properties
            pro = {}
            try:
                res = root.find('Object').find('Resources')
                for child in res.findall('Item'):
                    pp = child.find('Name')
                    pro[pp.text]=None
            except KeyError:
                pro = {}
            meta = ThingAttribute(**met)
            props = ThingAttribute(**pro)
            actns = ThingAttribute(**pro)
            thing = Thing(meta,props,actns)
            return thing

    def __init__(self):
        ThingFactory.factories = {0x00:ThingFactory.W3CFactory(), 0x01:ThingFactory.OCFFactory(), 0x02:ThingFactory.IPSOFactory()}

    #create the thing in here
    def CreateThing(self, namespace, url, ninterface):
        factory = ThingFactory.factories[namespace]
        return factory.CreateThing(url, ninterface)
        


