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

from Configurations import Config
import json
class ThingAttribute:
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

class Thing:
    def __init__(self, metd, props, behavs):
        self.mdata = metd
        self.attrs = props
        self.actns = behavs
        self.mdata.activeTime = Config.DefaultKeepAlive

    def addAttr(self, name, value):
        self.attrs.__setattr__(name,value)

    def addActn(self,name, value):
        self.actns.__setattr__(name,value)

    def writeAct(self,actn,value):
        self.actns.__setattr__(actn,value)

    def toJson(self):
        return '{"mdata":'+json.dumps(self.mdata.__dict__)+',"attrs":'+json.dumps(self.attrs.__dict__)+', "actns":'+json.dumps(self.actns.__dict__)+" }"

    


if __name__ == "__main__":
    meta = ThingAttribute(uid='st001',name='Smart Thermostat', type='Thermostat')
    props = ThingAttribute(humidity='33.8%', location='23.2332,22.456')
    actns = ThingAttribute(acstatus='false', minhumidity='20%',setHumidity='25%')
    thing = Thing(meta,props,actns)
    thing.addAttr('unit','degree_cel')
    thing.addActn('settemp','25.0')
    print(thing.toJson())
    thing.writeAct('settemp','23.0')
    print(thing.toJson())

