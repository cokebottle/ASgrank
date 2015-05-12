#!/usr/bin/python
'''
Description: A tool to query the mongodb AS database and build the graph with peers and BGPrank of each peer. Out can be to Gephi format.
Prerequisites: pymongo, json, networkx, matplotlib 


'''
__author__= 'Cosmin Ciobanu, Romain Bourgue, Razvan Gavrila'
__license__ = 'GPL'
__contact__ = 'cosmin.ciobanu at gmail dot com'
__version__ = 1.0

import pymongo,json
import sys
import networkx as nx
import matplotlib.pyplot as plt

#setup MongoDB database connection 
connect = pymongo.MongoClient("localhost", 27017)
db = connect.asnum

G=nx.Graph()

#Declare empty node dictionary and empty list of links
nodes={}
links=[]

#Query database
results = db.asDB.find()
i=0
for res in results: #iterate through the results fron database
    i=1+i
    print "Doing %s of %s asn" % (i,results.count())
    if(res['bgprank']!=None):
	G.add_node(res["asn"], country = res["country"], rank = float(res['bgprank'])) #populate graph nodes
    else:
	G.add_node(res["asn"], country = res["country"], rank = 0)
    j=0
    for peer in res["peers"]:
        j=j+1
        print "Doing %s of %s asn" % (j,len(res["peers"]))
        
        peer_obj=db.asDB.find_one({"asn":peer})
        
        if(peer_obj!=None):
            G.add_edge(res["asn"], peer)
        else:#unstored asn
            print "No record for asn %s" % peer
            #G.add_edge(res["asn"], peer, weight=2)   #populate graph edges

nx.write_gexf(G, "EUbadboys.gexf")
#print G.number_of_nodes()
#print G.number_of_edges()




#        nodes[res["asn"]]={"name":res["asn"],"group":res["country"], "rank":res["bgprank"]} #populate the node dictionary    
#        for peer in res["peers"]:
#            links.append({'source':res["asn"], "target":peer, 'value':1})
        
#print json.dumps({"nodes":nodes,"links":links}) 



#f=open("ASRomania.json", "w")
#f.write(json_d3js)
#f.close
