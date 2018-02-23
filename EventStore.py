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
import threading
import Configurations
from enum import Enum
from ThingAttribute import Thing
import redis
import json

class ThingEvent:
    def __init__(self, name, thing):
        self.Name = name
        self.Thing = thing

    def Set(self):
        self.rconn = redis.StrictRedis(host='localhost', decode_responses=True)
        if isinstance(self.Thing,str):
            self.rconn.publish(self.Name,self.Thing)
        elif isinstance(self.Thing, Thing):
            self.rconn.publish(self.Name,self.Thing.toJson())


class EventStore(threading.Thread):
    def __init__(self, resque):
        threading.Thread.__init__(self,daemon=True)
        self.rconn = redis.StrictRedis(host='localhost', decode_responses=True)
        self.epubsub = self.rconn.pubsub()
        self.rqueue = resque
        self.Store = {"3344":{"weather-station":["thingCreated","thingRemoved","thingUpdated"]}}
        #Structure of Store is dictionary of dictionaries where the inner ones are 
    
    def run(self):
        self.epubsub.subscribe('thingCreated', 'thingUpdated', 'thingRemoved')
        while True:
            pub = self.epubsub.get_message()
            if pub and isinstance(pub['data'], str):
                evtData = json.loads(pub['data'])
                self.handle(pub['channel'], evtData)
                
    def subscribe(self, pthingId, subs):
        self.Store[pthingId] = subs

    def receiveRequest(self, rqstUrl, reqstBody):
        sdata = json.loads(rqstBody)
        for key in sdata:
            subs = "{"+rqstUrl+":["+str(sdata[key])+"]}"#Assumes the subscription body is like 'pthingId':"coma,sepa,evts"
            self.subscribe(key, subs)
        #Extract the subscription information from the request body
        

    #example of sub => {'pubThing':{'subThing':[channnels]}}
    def unsubscribe(self, sthingId, pthingId, channels=None):
        if channels is None:#remove the whole thingId
            del self.Store[pthingId][sthingId]
        else:
            chnlsub = self.Store[pthingId][sthingId] #all subscribed channels
            for item in channels:
                chnlsub.remove(item)
            self.Store[pthingId][sthingId] = chnlsub
            
    
    def handle(self, channel, evntData):
        pthng = evntData.get('mdata').get('uid')
        subs = self.Store.get(pthng)
        if subs is not None:
            for thng in subs:
                if channel in subs[thng]:
                    print(thng,"notified for",channel,"on thing Id",pthng)
                    #Notify the subscriber about the event with responose



if __name__ == '__main__':
    es = EventStore()
    print('Listening for published messages')
    es.run()