# repeated_sale.py
me
# python to create a repeated sale price index
# Tom Davidoff
# 05/31/20

import os
import numpy as np
import math
import matplotlib.pyplot as plt

def drop_internal_comma(textline):
	newline = ""
	l = textline.split('"')
	for k in range(0,len(l)):
		old = l[k]
		if len(old)>0:
			if old==",":
				new=old
			else:
				if not int(k/2)==(k/2):
					# just first, third,...
					new=old.replace(',',';')
				else:
					new=old
			newline=newline+new
	return(newline)

solds= {}
heads = []
for  type_dir in ["Downloads/roomvu/detached/"]:# ,"Downloads/roomvu/attached/"]:
	for y in range(2000,2019):
		print("YEAR: ",y)
		y_dir = type_dir+str(y)+"/"
		files = os.listdir(y_dir)
		for f in files:
			df = open(y_dir+f,"r")
			head = df.readline().strip().replace('"','').split(',')
			if not head in heads:
				heads.append(head)
			['"PicCount","ML #","Status","P.I.D.#","Address","Region","City","Area","S/A","List Price","Price","Sold Price per SqFt","List Date","Sold Date","DOM","Tot BR","Tot Baths","TotFlArea","Yr Blt","Age","Frontage - Feet","Depth","#Kitchens","TypeDwel","Style of Home","Units in Development","Commission","Days On MLS","DDF More Info URL","Fake Listing","Fixt Rntd/Lsd - Specify","Floorplan URL","Gross Taxes","Lot Sz (Sq.Ft.)","Municipality","Parking Places - Total","Prev Commission","Prev Price","Property Brochure URL","Protected Owner Name","Public Remarks","Rain Screen","Realtor Remarks","Restricted Age","Sold Price","Strata Maint Fee","Title to Land","Virtual Tour URL","Zoning","Broker Reciprocity","List Desig Agt 1 - Agent Full Name","List Desig Agt 1 - LastTransDateMLX","List Desig Agt 1 - CREA ID","List Desig Agt 1 - License ID","List Desig Agt 2 - Agent Full Name","List Desig Agt 2 - CREA ID","List Desig Agt 2 - License ID","List Desig Agt 3 - Agent Full Name","List Desig Agt 3 - CREA ID","List Desig Agt 3 - E-mail","Sell Sales Rep 1 - Agent Full Name","Sell Sales Rep 1 - CREA ID","Sell Sales Rep 1 - License ID","Sell Sales Rep 2 - Agent Full Name","Sell Sales Rep 2 - CREA ID","Sell Sales Rep 3 - Agent Full Name","Sell Sales Rep 3 - CREA ID","Suite","Basement Area-Separate Entry","List Firm 1 Code - Office Name","List Firm 1 Code - LastTransDateMLX","List Firm 2 Code - Office Name","List Firm 2 Code - LastTransDateMLX","Selling Office 1 - Office Name","Selling Office 1 - LastTransDateMLX","Selling Office 2 - Office Name","Selling Office 2 - LastTransDateMLX","Postal Code"\n']
			for line in df:
				l = drop_internal_comma(line).strip().split(',')
				pid = l[head.index("P.I.D.#")]
				try:
					price_level = float(l[head.index("Sold Price")].replace('$','').replace(';',''))
					if price_level > 100000 and price_level < 50000000:
						price = np.log(price_level)
						date = l[head.index("Sold Date")].split("/")
						if len(date)==3:
							month = int(date[0])
							quarter = np.ceil(month/3)
							market = l[head.index("S/A")]
							if not pid in solds:
								solds[pid] = {"date":[],"rank":[],"price":[],"market":market}
								rank = 0
							else:
								rank = max(solds[pid]["rank"])+1
							solds[pid]["date"].append(y+(quarter-1)/4)
							solds[pid]["rank"].append(rank)
							solds[pid]["price"].append(price)
				except ValueError:
					pass

DO_SMALL = 1

length_bucket_info = {}
bucket_info = {}
big_bucket_info = {}
for pid in solds:
	l = solds[pid]
	sa = l["market"]
	R = max(l["rank"])
	if R>0:
		r = R
		while r>0:
			delta_p = (l["price"][r]-l["price"][r-1])
			length = l["date"][r]-l["date"][r-1]
			if length not in length_bucket_info:
				length_bucket_info[length] = {"gains":[]}
			length_bucket_info[length]["gains"].append(delta_p)
			if DO_SMALL==1:
				
				bucket = sa + "," + str(l["date"][r]) + "," + str(l["date"][r-1])
				if bucket not in bucket_info:
					bucket_info[bucket] = {"gains":[],"length":length,"market":sa}
				bucket_info[bucket]["gains"].append(delta_p)
				big_bucket = str(l["date"][r]) + "," + str(l["date"][r-1])
				if big_bucket not in big_bucket_info:
					big_bucket_info[big_bucket] = {"gains":[],"length":length,"market":sa}
				big_bucket_info[big_bucket]["gains"].append(delta_p)
			r = r-1

t_vec = []
sd_vec = []
	
for K in range(41):
	k = K/4
	print(k)
	sk = math.sqrt(k)
	print([k,sk,len(length_bucket_info[k]["gains"]),np.mean(length_bucket_info[k]["gains"])/k,np.std(length_bucket_info[k]["gains"])])
	t_vec.append(k)
	sd_vec.append(np.std(length_bucket_info[k]["gains"]))
	if DO_SMALL==1:
		bucket_gains = []
		bucket_sds = []
		big_bucket_gains = []
		big_bucket_sds = []
		for bucket in bucket_info:
			if bucket_info[bucket]["length"]==k and len(bucket_info[bucket]["gains"])>5:
				bucket_gains.append(np.mean(bucket_info[bucket]["gains"]))
				bucket_sds.append(np.std(bucket_info[bucket]["gains"]))
		print(["MICRO:",k,sk,np.mean(bucket_gains)/k,np.median(bucket_sds),np.std(bucket_gains)])
		for bucket in big_bucket_info:
			if big_bucket_info[bucket]["length"]==k and len(big_bucket_info[bucket]["gains"])>5:
				big_bucket_gains.append(np.mean(big_bucket_info[bucket]["gains"]))
				big_bucket_sds.append(np.std(big_bucket_info[bucket]["gains"]))
		print(["MACRO:",k,sk,np.mean(big_bucket_gains)/k,np.median(big_bucket_sds),np.std(big_bucket_gains)])


plt.scatter(t_vec,[.05*math.sqrt(t) for t in t_vec])
plt.scatter(t_vec,sd_vec)
plt.xlabel("Holding Period")
plt.ylabel("Std of individual nominal gains")
plt.title("Vancouver MLS repeated sales analysis 2000-2019")
plt.legend()
plt.savefig("Documents/rmfix/text/t_sd.png")
plt.close()

