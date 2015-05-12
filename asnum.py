#!/usr/bin/python
"""
A tool for quering RIPE api obtain AS peer information, query CIRCL BGPrank and obtain reputation rank

"""
__author__= 'Cosmin Ciobanu, Romain Bourgue, Razvan Gavrila'
__license__= 'GPL'
__contact__= 'cosmin.ciobanu@gmail.com'
__version__ = 1.0

#import modules
import pymongo,json, time
import bgpranking_web
import argparse
import sys
import socket
import urllib2


#setup database connection 
connect = pymongo.MongoClient("localhost", 27017)
db = connect.asnum
#select collection from MongoDB
#EU_memberstates = ["AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GB", "GR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"]
EU_memberstates = ["RO"]
asnlist = {}


class Asnode:
   def jsonable(self):
      return self.__dict__
   pass


#function to query RIPE api for country AS information
def countryQueryRipe(country = None):
    print "Quering RIPE API for Country"+ country + "\n"
    response = json.load(urllib2.urlopen('http://stat.ripe.net/data/country-resource-list/data.json?resource='+ country +'&resources=as'))
    #countryJson = json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')) #print formatted json
    results = response["data"]["resources"]["asn"]
    res=[]
    for item in results:#fix me later
        res.append(int(item))
    return res #[132,4654,6546,3513]
    #db.country.insert(response)
    
def peerQueryRipe(asnumber = None):
    print "Quering RIPE API for AS"+ str(asnumber) + " peers\n"
    response = json.load(urllib2.urlopen('http://stat.ripe.net/data/asn-neighbours/data.json?resource=AS'+str(asnumber)))
    peerlist=[]
    for neighbour in response["data"]["neighbours"]:
        peerlist.append(neighbour["asn"])
    return peerlist
    #print response["data"]["neighbours"][0]["asn"]
    #print json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')) #print formatted json

#function to query BGPrank api
def queryBgprank(query = None):
    data = bgpranking_web.cached_daily_rank(query)
    return data[4]
#    print 'Received', repr(data)

#function to query TeamCymru IP2ASN
def queryTeamCymru(query = None):
    HOST = 'whois.cymru.com'    # The remote services host
    PORT = 43                 # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    #print query
    s.send(" -v" + query + "\r\n") #Send ASNumber and query for reputation information
    data = s.recv(1024)
    s.close()
    data = data.split("\n") #Split by new-line into array and print second line

#next step geolocation plotting: https://stat.ripe.net/data/geoloc/data.json?resource=9050


#start main()

if __name__== "__main__":
    
    for country in EU_memberstates:
        #queryBgprank("9050")
        #queryTeamCymru("9050")
        asnList=countryQueryRipe(country)#returns a list of ASN for a country
        
        #don't query the ASNs with lastupdate < time-1d
        
        dontCheck=db.asDB.find({"country":country , "lastupdate":{"$gt":time.time()-168*3600}})
        
        i=0
        for AS in dontCheck:
            i=i+1
            asnList.remove(AS["asn"])
        print "Removed %i AS with fresh info" % i

        i=0
        for asnum in asnList:
            i=i+1
            print "Querying AS %i / %i" % (i,len(asnList))
            asnode=Asnode()
            #Populate the object
            asnode.asn=asnum
            asnode.name="AS"+str(asnum)
            asnode.country=country
            asnode.peers=peerQueryRipe(asnum)
            asnode.bgprank=queryBgprank(asnum)
            asnode.lastupdate=time.time()
            db.asDB.remove({"asn":asnum})
            db.asDB.insert(asnode.__dict__)
            
    
    col= db.asDB.find()
    for doc in col:
        print doc
        #peerQueryRipe("9050")
      
        
    
    
