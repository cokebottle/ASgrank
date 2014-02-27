##ASgrank a.k.a. AS number peer graphs and ranking
###Prerequisites
```
MongoDB, PyMongo, NetworkX, argparse, json
```
asnum.py 
Queries RIPE API for AS belonging to particular countries
For each AS number of country queries for peers and for each AS + peers queries BGPrank for reputation rank.

```
graphbuild.py
Creates the graph of peerings along with BGPRank of each AS.
```
![Graph](http://raw.github.com/cokebottle/ASgrank/master/cool_weighted.png)

