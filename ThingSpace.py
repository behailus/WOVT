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
  
This is a space for the 'Thing' Agents to interact and live as long as the time to live doesn't expire. 
'''
from ThingAttribute import Thing
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from Configurations import Config
from EventStore import ThingEvent
import json
import threading
import queue
import redis

class ThingRequestHandler(BaseHTTPRequestHandler):
    notexist = {}
    resque = None
    rconn = redis.StrictRedis(host='localhost',decode_responses=True)
    def do_GET(self):
        logging.debug("GET request, Path = " + str(self.path))
        tuid = self.path.split('/')[-1]#take the last part of the url
        if tuid != '':
            thg = ThingRequestHandler.rconn.get(tuid)
            if(thg != None):
                self.SetHeaderSuccess()
                self.wfile.write(bytes(str(thg), "utf-8"))
            else:
                self.SetHeaderFailed()
                ThingRequestHandler.notexist['error'] = 'This thing id does not exist'
                self.wfile.write(bytes(json.dumps(ThingRequestHandler.notexist), "utf-8"))

        else:
            self.SetHeaderSuccess() 
            thgkeys = {'things':ThingRequestHandler.rconn.keys()}
            self.wfile.write(bytes(json.dumps(thgkeys), "utf-8"))

    def do_POST(self):
        tuid = self.path.split('/')[-1]#take the last part as thing UID
        data = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
        try:
            tdata = json.loads(data)
            thg = ThingRequestHandler.rconn.get(tuid)
            if thg != None:
                obj = json.loads(thg)
                for key in tdata:
                    obj['actns'][key] = tdata.get(key)
                
                thg = json.dumps(obj)
                ThingRequestHandler.rconn.set(tuid,thg)
                evt = ThingEvent('thingUpdated',thg)
                evt.Set()
                ThingRequestHandler.resque.put({tuid:data})
                self.SetHeaderSuccess()
                self.wfile.write(bytes(str(thg), "utf-8"))
            else:
                self.SetHeaderFailed()
                ThingRequestHandler.notexist['error'] = 'Invalid thing URL'
                self.wfile.write(bytes(json.dumps(ThingRequestHandler.notexist), "utf-8"))


        except Exception as ex:
            self.SetHeaderFailed()
            ThingRequestHandler.notexist['error'] = 'Invalid operation '+str(ex)
            self.wfile.write(bytes(json.dumps(ThingRequestHandler.notexist), "utf-8"))

        
    def SetHeaderSuccess(self):
        self.send_response(200)
        self.send_header('Content-type','text/json')
        self.end_headers()

    def SetHeaderFailed(self):
        self.send_response(404)
        self.send_header('Content-type','text/json')
        self.end_headers()

class Space(threading.Thread):
    def __init__(self, resQue):
        threading.Thread.__init__(self,daemon=True)
        self.dbconn = redis.StrictRedis(host='localhost', decode_responses=True)
        self.rqueue = resQue
    def NewThing(self, thing):
        logging.debug("Thing space added new thing")
        self.dbconn.set(str(thing.mdata.uid), thing.toJson())
        evt = ThingEvent('thingCreated', thing)
        evt.Set()
        
    def UpdateThing(self, thing):
        self.dbconn.set(str(thing.mdata.uid), thing.toJson())
        logging.debug("Thing space updated thing")

    def RemoveThing(self, thing):
        self.dbconn.delete(str(thing))
        logging.debug("Thing space removed thing")


    def run(self):
        logging.debug("HTTP Server started")
        ThingRequestHandler.resque = self.rqueue
        tsHttpServer = HTTPServer((Config.TSHOST,Config.TSPORT),ThingRequestHandler)
        try:
            tsHttpServer.serve_forever()
        except KeyboardInterrupt:
            pass
        tsHttpServer.server_close()
        logging.debug("HTTP Server closed")

