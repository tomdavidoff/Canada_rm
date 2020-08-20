# crea_vancouver.py
# python to get sd by year of Vancouver
# Tom Davidoff
# 08/12/20

import numpy as np

for name in ["vancouver","toronto","calgary","ottawa","montreal"]:

	for k in [1,2,3,4,5]:
		a = open("Documents/rmfix/data/crea_"+name+".csv","r")
		head = a.readline().split(",")
		prices = {}
		years = []
		gains = []
		for line in a:
			if 'Jan' in line:
				l = line.split(",")
				year = int(l[0].split(" ")[1])
				if (year/k)==int(year/k):
					prices[year] = float(l[head.index("Composite_HPI")])
					years.append(year)

		for j in range(min(years)+k,max(years)+1):
			if (j/k)==int(j/k):
				gains.append(np.log(prices[j]/prices[j-k]))

		#print(gains)
		print([name,k,np.std(gains)])

g = open("Documents/rmfix/data/teranet.csv","r")
head = g.readline().strip().split(",")
g.close
#Transaction Date,bc_victoria,bc_vancouver,mb_winnipeg,qc_montreal,qc_quebec_city,ns_halifax
for j in ["bc_victoria","bc_vancouver","mb_winnipeg","qc_montreal","qc_quebec_city","ns_halifax"]:
	for k in [1,5]:
		g = open("Documents/rmfix/data/teranet.csv","r")
		g.readline()
		g.readline()
		prices = {}
		years = []
		gains = []
		for line in g:
			if "Jul-1990" in line: # close enough
				line = line.replace("Jul","Jun")
			if "Jun-" in line:
				year = int(line.split("-")[1].split(',')[0])
				index = float(line.split(",")[head.index(j)])
				if (year/k)==int(year/k):
					prices[year] = index
					years.append(year)

		for m in range(min(years)+k,max(years)+1):
			if (m/k)==int(m/k):
				gains.append(np.log(prices[m]/prices[m-k]))

		#print(gains)
		print([j,k,np.std(gains)])



# now try FHFA San Francisco

horizons = [1,4,9]
sds = {x:[] for x in horizons}

metros = []
a = open("/home/davidoff/Documents/rmfix/data/HPI_AT_metro_20_1.txt")
for line in a:
	metro = line.split("\t")[1]
	if not metro in metros:
		metros.append(metro)

MINYEAR = 1980
for k in horizons:
	for m in metros:
		a = open("/home/davidoff/Documents/rmfix/data/HPI_AT_metro_20_1.txt")
		#"Abilene, TX"	10180	1975	1	-	-
		prices = {}
		years = []
		gains = []
		for line in a:
			l = line.split("\t")
		#	if "San Francisco" in line and not l[4]=="-":
			if l[1]==metro and not l[4]=="-":
				quarter = int(l[3])	
				if quarter==1:
					year = int(l[2])		
					if year>=MINYEAR and (year/k)==int(year/k):
						prices[year] = float(l[4])
						years.append(year)

		print(min(years),k)
		for j in range(min(years)+k,max(years)+1):
			if (j/k)==int(j/k):
				gains.append(np.log(prices[j]/prices[j-k]))

		#print(gains)
		sds[k].append(np.std(gains))

for k in sds:
	print("THIS IS"+str(k))
	print(np.mean(sds[k]))


