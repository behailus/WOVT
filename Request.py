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


''' Request format
    +---------------------------------------------------------------+
    |0      1       2       3       4       5       6       7       |
    |_______________________________________________________________|
0   | Version                      |      Verb     | Accept | Notify|
    |______________________________|________________________________|
1   |                 Payload size (0 for GET)                      |
    |_______________________________________________________________|
2   |     Protocol id              |       namespace(4 bits)        |
    |______________________________|________________________________|
3   |                    resource url (l byte)                      |
    |_______________________________________________________________|
3+l |                           body                                |
n   |_______________________________________________________________|

*NEW: Namespace: for datamodel namespaces (0x00: W3C, 0x01:OIC, 0x02: IPSO)
'''
import logging
from Utils import RequestMethods
#requestFormat
class Request:
    def __init__(self,blob):
        self.content = blob
        self.tryBuild()

    def tryBuild(self):
        self.verb = self.getMethod()
        self.version = self.getVersion()
        self.accept = self.getAccept()
        self.subscribe = self.getSubscribe()
        self.namespace = self.getNamespace()
        self.bodyLength = self.getLength()
        self.resourceUrl = self.getResourceUrl()
        self.body = self.getBody()
        logging.debug("Requested parsed properly")

    def getVersion(self):
        fstbyte = self.content[0]
        return ((fstbyte & 0xF0) >> 4)

    def getMethod(self):
        fstbyte = self.content[0]
        mtd = ((fstbyte & 0x0C) >> 2)
        sub = self.getSubscribe()
        if mtd == 0 and sub == 0:
            return RequestMethods.GET
        elif mtd == 0 and sub == 1:
            return RequestMethods.NOTIFY
        elif mtd == 1:
            return RequestMethods.POST
        elif mtd == 2:
            return RequestMethods.DELETE

    def getAccept(self):
        fstbyte = self.content[0]
        return ((fstbyte & 0x02) >> 1)

    def getSubscribe(self):#Same as notify
        fstbyte = self.content[0]
        return (fstbyte & 0x01)
        
    def getLength(self):
        scndbyte = self.content[1]
        return scndbyte
    def getNamespace(self):
        return (self.content[2] & 0x0F)

    def getProtocolId(self):
        return (self.content[2] & 0xF0)

    def getResourceUrl(self):
        if self.bodyLength == 0:
            return (''.join(map(chr,self.content[3:])))
        else:
            tl = len(self.content)
            return (''.join(map(chr,self.content[3:tl-self.bodyLength])))
        
    def getBody(self):
        if self.bodyLength == 0:
                return ''
        else:
            tl = len(self.content)
            return (''.join(map(chr,self.content[tl-self.bodyLength:])))
