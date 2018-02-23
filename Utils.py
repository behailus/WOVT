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
import json
import xml.etree.cElementTree as eTree
from enum import Enum
import ramlfications
#Custom response code for requests
class ResponseCode(Enum):
    Continue = 100
    OK       = 200
    Created  = 201
    Accepted = 202

    BadRequest = 40
    Forbidden  = 43
    NotFound   = 44
    RequestTimeout    = 48

class RequestMethods(Enum):
    GET = 0
    POST = 1 
    NOTIFY = 1
    DELETE = 2

    #others will be added when needed

class Parser:
  def __init__(self, url, ptype):
    self.type = ptype
    self.url = url
  
  def Parse(self):
      if self.type == 'JSON':
          data = None
          with open(self.url+'.json') as df:
              data = json.load(df)
          return data
      
      elif self.type == 'XML':
          tree = eTree.ElementTree(file=self.url+'.xml')
          return tree


if __name__ == "__main__":
    pars = Parser('models/ipso/3344','XML')
    #pars = Parser('models/ocf/oic.r.sensor.activity.count','JSON')
    #pars = Parser('models/w3c/weather-station','JSON')
    test = pars.Parse()
    root = test.getroot() 
    #for ipso
    print('Metadata')
    print('_______________')
    res = root.find('Object')
    name = res.find('Name')
    print("Name : %s" % (name.text))
    
    print("properties")
    print('_______________')
    res = root.find('Object').find('Resources')
    for child in res.findall('Item'):
        pp = child.find('Name')
        print(pp.text)
    '''#for ocf
    del test['id']
    del test['$schema']
    del test['description']
    print('Metadata')
    print('_______________')
    for key in test:
        if not (type(test[key]) == dict or type(test[key])==list):
            print("%s : %s" % (key, test[key]))
    print("properties")
    print('_______________')
    prop = test['definitions']
    for p in prop:
        ppts = prop[p]['properties']
        for pp in ppts:
            print(pp)
    '''
    '''#for w3c
    del test['@context']
    del test['@type']
    print('Metadata')
    print('_______________')
    for key in test:
        if not (type(test[key]) == dict or type(test[key])==list):
            print("%s : %s" % (key,test[key]))
    print("properties")
    print('_______________')
    prop = test['interactions']
    for p in prop:
        print(p['name'])

    '''
