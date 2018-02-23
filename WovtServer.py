#main entry to the ISSServer
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
import os
import sys
import logging
import threading
import queue
import time
import random
from abc import ABCMeta, abstractmethod
from Rdfhandler import NameResolver 
from Configurations import Config
from Request import Request
from Response import Response
from ThingFactory import ThingFactory
from ThingRegistry import Registry
from ThingSpace import Space
from Utils import RequestMethods
from EventStore import EventStore
#from nrf24 import NRF24
class NetworkInterface:
    __metaclass__=ABCMeta
    @abstractmethod
    def __init__(self,code,name,datarate,confirmed=False):
        pass

    @abstractmethod
    def begin(self): pass

    @abstractmethod
    def start_listening(self): pass

    @abstractmethod
    def message_available(self):pass

    @abstractmethod
    def stop_listening(self): pass

    @abstractmethod
    def send(self, destination, data): pass

    @abstractmethod
    def receive(self):pass

    @abstractmethod
    def reply(self):pass

    #Only for demo, generate requests
    def randMethod(self):
        return random.choice([RequestMethods.GET,RequestMethods.POST])

    def randModel(self):
        return random.choice([0x00,0x01,0x02])

    def randObject(self, model):
        if model == 0:
            return random.choice(os.listdir(Config.W3CModelRoot))
        elif model == 1:
            return random.choice(os.listdir(Config.OCFModelRoot))
        elif model == 2:
            return random.choice(os.listdir(Config.IPSOModelRoot))

    def getBody(self, model, path):
        fact = ThingFactory()
        thng = fact.CreateThing(model, path, self.name)
        body = "{"
        n = random.randrange(0,100)
        for pr in thng.attrs.__dict__:
            body += ('"'+str(pr) + '":"' + random.choice(["True", "False", str(n)])+'",')
        if len(body) > 1:
            body = body[:-1]
        body += "}"
        return body

    def randBuildRequest(self):
        version = 0
        notify = 0#random.choice([0,1])
        model = random.choice([0,1,2])#data model
        url = self.randObject(model)
        extn = url.split('.')[-1]
        rpath = url[0:(len(url)-len(extn)-1)]
        verb = self.randMethod()
        body = ""
        b1 = 0
        b2 = 0
        if verb == RequestMethods.GET:
            b1 = (version << 4) | (verb.value << 2) | notify #
        else:
            b1 = (version << 4) | (verb.value << 2)
            body = self.getBody(model, rpath)

        b2 = len(body)
        b3 = self.code | model 
        rqst = []
        rqst.append(b1)
        rqst.append(b2)
        rqst.append(b3)
        rqst  = rqst + [ord(c) for c in rpath]
        if b2 > 0:
            rqst = rqst + [ord(c) for c in body]
        return rqst

class BleInterface(NetworkInterface):
    def __init__(self,code,name,datarate,confirmed=False):
        self.code = code
        self.name = name
        self.datarate = datarate
        self.confirmed = confirmed
        self.source = ''
    def begin(self):
        logging.debug('Ble interface started')
        '''BLE related initialization goes here
        '''
    def start_listening(self):
        logging.debug('Ble interface started listening')

    def stop_listening(self):
        logging.debug('Ble interface stoped listening')

    def message_available(self):
        return True
        
    def send(self, destination, data):
        logging.debug('Ble interface message sent')

    def receive(self):
        logging.debug('Ble interface received message')        
        return self.randBuildRequest() #[0x00, 0x00, 0x21, 0x73, 0x65, 0x6e, 0x73, 0x6f, 0x72, 0x2e, 0x61, 0x63, 0x74, 0x69, 0x76, 0x69, 0x74, 0x79, 0x2e, 0x63, 0x6f, 0x75, 0x6e, 0x74]

    def reply(self,data):
        if(isinstance(data,Response)):
            logging.debug(data.responseCode)
            logging.debug(data.checksum)
            logging.debug(data.remains)
            logging.debug(data.body)

class NrfInterface(NetworkInterface):
    def __init__(self,code,name,datarate,confirmed=False):
        self.code = code
        self.name = name
        self.datarate = datarate
        self.confirmed = confirmed
        self.pipes = [[0xA2,0xA2,0xA2,0xA2,0xA2],[0x20,0x20,0x20,0x20,0x20]]
        self.source = ''
    def begin(self):
        #begin nrf module and initialize
        logging.debug('Nrf interface started')
        '''self.radio = NRF()
        self.radio.begin(0, 0, 7, 8)
        self.radio.setPayloadSize(32)
        self.radio.setChannel(0x60)
        self.radio.setDataRate(NRF24.BR_250KBPS)
        self.radio.setPALevel(NRF24.PA_MAX)
        self.radio.openWritingPipe(self.pipes[1])
        self.radio.openReadingPipe(self.pipes[0])
        '''
    def start_listening(self):
        logging.debug('Nrf interface started listening')
        #self.radio.startListening()

    def stop_listening(self):
        logging.debug('Nrf interface stoped listening')
        #self.radio.stopListening()

    def message_available(self):
        return True
        #lp = [0]
        #return self.radio.available(lp,False)
        
    def send(self, destination, data):
        logging.debug('Nrf interface message sent')
        #send the data, stop listening and write
        #self.radio.write(data)

    def receive(self):
        logging.debug('Nrf interface received message')       
        return self.randBuildRequest() #[0x00, 0x00, 0x10, 0x77, 0x65, 0x61, 0x74, 0x68, 0x65, 0x72, 0x2d, 0x73, 0x74, 0x61, 0x74, 0x69, 0x6f, 0x6e]

    def reply(self,data):
        #self.radio.write(data)
        if(isinstance(data,Response)):
            logging.debug(data.responseCode)
            logging.debug(data.checksum)
            logging.debug(data.remains)
            logging.debug(data.body)

class TcpIpInterface(NetworkInterface):
    def __init__(self,code,name,datarate,confirmed=False):
        self.code = code
        self.name = name
        self.datarate = datarate
        self.confirmed = confirmed
        self.pipes = [[0xA2,0xA2,0xA2,0xA2,0xA2],[0x20,0x20,0x20,0x20,0x20]]
        self.source = ''
    def begin(self):
        #begin nrf module and initialize
        logging.debug('Tcp/Ip interface started')

    def start_listening(self):
        logging.debug('Tcp/Ip interface started listening')
        #self.radio.startListening()

    def stop_listening(self):
        logging.debug('Tcp/Ip interface stoped listening')
        #self.radio.stopListening()

    def message_available(self):
        return True
        #lp = [0]
        #return self.radio.available(lp,False)
        
    def send(self, destination, data):
        logging.debug('Tcp/Ip interface message sent')
        #send the data, stop listening and write
        #self.radio.write(data)

    def receive(self):
        logging.debug('Tcp/Ip interface received message')        
        return self.randBuildRequest()
        '''m = self.randMethod()
        if m == RequestMethods.GET:
            return [0x00, 0x00, 0x32, 0x33,0x33,0x34,0x34]
        elif  m == RequestMethods.POST:
            return [0x04, 0x04, 0x32, 0x33, 0x33, 0x34, 0x34, 0x74, 0x65, 0x73, 0x74]'''

    def reply(self,data):
        #self.radio.write(data)
        if(isinstance(data,Response)):
            logging.debug(data.responseCode)
            logging.debug(data.checksum)
            logging.debug(data.remains)
            logging.debug(data.body)
   
#Network communication handler
class TransportHandler(threading.Thread):
    def __init__(self, qu, rsq):
        threading.Thread.__init__(self,daemon=True)
        self.interfaces = {}
        self.rqueue = qu #request queue for network interface to pass the incoming message
        self.rsqueue = rsq #response queue
    def addInterface(self, name, ifobject):
        self.interfaces[name] = ifobject

    def initialize(self):
        for key,val in self.interfaces.items():
            val.begin()
            val.start_listening()
            
    def run(self):
        msg = []
        while(1):
            for key,val in self.interfaces.items():
                if val.message_available():
                    msg = val.receive()
                    request = Request(msg)
                    self.rqueue.put((val,request))
                    logging.debug("Message put in request queue by "+key)
                    blob = ' '.join(hex(c) for c in msg)
                    logging.debug("Message : "+blob)
                else:
                    if not self.rsqueue.empty():#there is an outgoing response -> how to send back? make the interfaces
                        #accessible separately vs let transport handler manage out going as well
                        rspn = self.rsqueue.get()
                time.sleep(0.05)#sleep for 1s not necessary in production

#Request handler for dss server
class RequestHandler:
    def __init__(self, version, storePath, rdfpath, rsqueue):
        self.responseq = rsqueue
        self.version = version
        self.storePath = storePath
        self.resourceTree()
        self.resolver = NameResolver(rdfpath)#make it configurable
        self.resolver.begin()

    def handle(self,request, transport):
        #check the method and send to the right handler
        if self.checkVersion(request):
            if(request.verb == RequestMethods.GET): #GET
                self.handleGet(request, transport)
            elif(request.verb == RequestMethods.POST): #POST
                self.handlePost(request, transport)
            elif(request.verb == RequestMethods.NOTIFY): #Notify
                self.handleNotify(request, transport)
    
    def checkVersion(self,request):
        return self.version == request.version
        
    def handleGet(self,request,transport):
        if self.checkVersion(request):
            fpath = self.getResource(request.resourceUrl)            
            if fpath == '':
                blob = [ResponseCode.NotFound,'']
                resp = Response(blob,0)
                transport.interface.reply(resp)
            else:            
                tsz = os.path.getsize(fpath)
                step = transport.interface.datarate
                count = 0
                f = open(fpath,'rb')
                while count < tsz:
                    count+=step
                    buff = f.read(step)
                    if count < tsz:
                        blob = [ResponseCode.Continue,buff]
                        resp = Response(blob,tsz-count)
                        transport.interface.reply(resp)
                    else:
                        blob = [ResponseCode.OK,buff]
                        resp = Response(blob,0)
                        transport.interface.reply(resp)
        else:
            blob = [ResponseCode.BadRequest,'']
            resp = Response(blob,0)
            transport.interface.reply(resp)

    def handlePost(self,request,transport):
        if self.checkVersion():
            found = False
            if not found:
                blob = [ResponseCode.NotFound,'']
                resp = Response(blob,0)
                transport.interface.reply(resp)
        
        else:
            blob = [ResponseCode.BadRequest,'']
            resp = Response(blob,0)
            transport.interface.reply(resp)        

    def handleNotify(self,request,transport):
        if self.checkVersion():
            found = False
            if not found:
                blob = [ResponseCode.NotFound,'']
                resp = Response(blob,0)
                transport.interface.reply(resp)

        else:
            blob = [ResponseCode.BadRequest,'']
            resp = Response(blob,0)
            transport.interface.reply(resp)            

    def resourceTree(self):
        self.resources = os.walk(self.storePath,topdown=True)
    
    def getResource(self,name):
        fpath = ''
        #fpath = self.resolver.Resolve(name)
        return self.storePath+fpath          
                    
#sample path /dss/shared/sample
logging.basicConfig(filename='wovt.log', level = logging.ERROR, format='%(asctime)s:%(levelname)s => %(message)s')

if __name__=="__main__":
    logging.debug(Config.DefaultKeepAlive)
        
    #DO INITIALIZATION HERE FIRST
    rq = queue.Queue() #message queue from the network interfaces
    rsq = queue.Queue() #Out going queue 
    tq = queue.Queue() #internal update
    interface1 = NrfInterface(0x10,'Nrf24',26,False) #interface 1
    interface2 = BleInterface(0x20, 'BT Smart',20,False) #interface 2
    interface3 = TcpIpInterface(0x30, 'TCP IP',65535,False) #interface 2
    
    transport = TransportHandler(rq,rsq)
    transport.addInterface(interface1.name,interface1)
    transport.addInterface(interface2.name,interface2)
    transport.addInterface(interface3.name,interface3)
    transport.initialize()

    handle = RequestHandler(0,'dss','models/iot-lite.rdf', rsq) #protocol handler
    tspace = Space(tq)
    tregistry = Registry()
    tfactory = ThingFactory()
    estore = EventStore(tq)
    
    transport.start() #start listening on all the initialized network interfaces
    tspace.start()
    logging.debug("Server started")
    estore.start()
    print("Server running...")
    #st = time.time()
    cntr = 0
    while(True):#run forever
        if(not rq.empty()):#if there is a request in the queue
            fullrqst = rq.get() #get the request from the queue - includes the transport
            rqst = fullrqst[1]
            cntr += 1
            logging.debug("Request url: "+rqst.resourceUrl)
            if tregistry.Instance.ThingAlive(rqst.resourceUrl):#if the thing is registered - POST/PUT
                logging.debug("Thing found in registry: "+rqst.resourceUrl)
                tregistry.Instance.Update(rqst.resourceUrl)
            else: #GET
                newThing = tfactory.CreateThing(rqst.getNamespace(), rqst.resourceUrl, fullrqst[0].name)
                tregistry.Instance.Register(newThing,tspace.NewThing) #send through 
                logging.debug("Created:"+str(newThing.toJson()))
            if rqst.verb == RequestMethods.GET:
                try:
                    handle.handle(rqst, fullrqst[0])
                except Exception as ex:
                    logging.debug("Unable to locate script for "+rqst.resourceUrl)
                logging.debug("Request GET")
            elif rqst.verb == RequestMethods.POST:#Check for notify flag to switch between update & subscriptions
                logging.debug("Request body "+rqst.body)
                if rqst.subscribe == 0:
                    tregistry.Instance.Modify(rqst.resourceUrl, rqst.body, tspace.UpdateThing)
                else:#It is a notification subscription and update it
                    estore.receiveRequest(rqst.resourceUrl, rqst.body)
            
        if(not tq.empty()):
            respUpdate = tq.get() #check if there is an outgoing message or update from thing space
            for key in respUpdate:
                tregistry.Instance.Modify(key, respUpdate[key]) #Update registry
        '''et = time.time()
        if (et- st) > 100:
            print(cntr)
            break'''
                #Send response put in rsq
        #tregistry.Instance.GarbageCollector(tspace.RemoveThing)#clean the registry
    


 


    
        