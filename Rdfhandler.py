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
import rdflib

class NameResolver:
    def __init__(self,rdfPath):
        self.rdfPath = rdfPath
    def begin(self):
        self.iotGraph = rdflib.Graph()
        self.iotGraph.parse(self.rdfPath)
    
    def Resolve(self,name):
        self.queryText = 'select ?s ?t where { <http://purl.oclc.org/NET/UNIS/fiware/iot-lite#'+name+'>  ?t  ?s}'
        result = self.iotGraph.query(self.queryText)
        if len(result) > 0:
            return result
            #for row in result:
            #    return row[0]
        else:
            return ''

'''if __name__ == "__main__":
    handlr = NameResolver('models/iot-lite.rdf')
    handlr.begin()
    reslt = handlr.Resolve('SampleWear')
    for r in reslt:
        print('%s <= %s'%r)'''