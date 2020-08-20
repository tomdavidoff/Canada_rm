# terminate_hecm.py
# python to handle hecm termation behavior
# Tom Davidoff
# 08/15/20

import pandas as pd 
import numpy as np
from multiprocessing import Pool	
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.iolib.summary2 import summary_col
from matplotlib import pyplot as plt


MAX_YEAR = 2011
MAX_MONTH = 11

df = pd.read_csv("Documents/rmfix/data/HECM_dataset_main_Nov11.csv",usecols=["case_id","borrower_age_orig","coborrower_age_orig","HECM_Type","init_prncpl_lmt","prprty_aprsl_vl","closing_date","mrgn_rt","prop_addr_zip_cd","termination_date"])

df = df[df.closing_date!="     ."]
print(df.describe())
print(df.mrgn_rt.describe())

zillow = pd.read_csv("Documents/rmfix/data/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_mon.csv")
z = list(zillow.columns)
for j in z:
	if "-" in j:
		z[z.index(j)] = "z"+j.split("-")[0]+j.split("-")[1]
zillow.columns = z
for zz in zillow.columns:
	print(zz)
	print(zillow[zz].describe())

df["RegionID"] = df.prop_addr_zip_cd

if 1>2:
	print(df.columns)
	df = df.merge(zillow,on="RegionID")
	print(df.columns)

t = pd.read_csv("Documents/rmfix/data/DGS1.csv")
t1 = {}
for d in set(t.DATE):
	try:
		t1["t"+d.split("-")[0]+d.split("-")[1]] = float(t["DGS1"][t.DATE==d])/1200
	except ValueError:
		pass


print(t1)

df["ltv"] = df["init_prncpl_lmt"].astype(float)/df["prprty_aprsl_vl"].astype(float)
print(df.ltv.describe())
df = df[df.ltv>0]

with open("Documents/rmfix/data/hecm_results.csv","w") as g:
	g.write("case_id,age,ltv,terminate,year,terminate_date\n")

	def do_term(case_id):
		rando = np.random.random()
		if rando>.5: # low sample prob
			j = case_id
			print(j)
			ltvs = []
			terminations = []
			ages = []
			line = df[df.case_id==j]
			zz = int(line.RegionID)
			if zz in set(zillow.RegionID):
				zline = zillow[zillow.RegionID==int(line.RegionID)]
				close = line["closing_date"].astype(int)
				terminate = line["termination_date"]
				start_year = int(close/100)
				if start_year > 1995 and start_year<2011:
					start_month = int(close)-100*start_year
					start_date = start_year*100 + start_month
					try:
						terminate_year = int(int(terminate)/100)
						terminate_month = int(int(terminate)-100*terminate_year)
					except ValueError:
						terminate_year = MAX_YEAR
						terminate_month = MAX_MONTH
					try:
						terminate_date = terminate_year*100 + terminate_month
						ltv = float(line.ltv)
						ltv_m = ltv
						start_zillow = float(zline["z"+str(int(start_date))])
						start_age = int(line["borrower_age_orig"])
						for y in range(start_year,terminate_year+1):
							print(y)
							if y==start_year:
								m0 = start_month+1
							else: 
								m0 = 1
							if y==terminate_year:
								m1 = terminate_month
							else:
								m1 = 12
							age = start_age+y-start_year
							print([y,m0,m1,j,start_year,terminate_year])
							for m in range(m0,m1+1):
								date = y*100+m
								if date < 201106:
									try:
										ltv = ltv*(1+float(t1["t"+str(date)])+float(line["mrgn_rt"])/1200)
										x = float(zline["z"+str(date)])
										print([x,ltv])
										ltv_m = float(ltv/(x/start_zillow)) # second line in case missing zillow
										term = 0
										if (date==terminate_date):
											term=1
										ltvs.append(ltv_m)
										terminations.append(term)
										ages.append(age)
										g.write(str(case_id)+","+str(age) + "," + str(ltv_m)+","+str(int(term)) +"," + str(y) + "," + str(terminate_date)+ "\n")
									except KeyError:
										pass # will get some weird stuff like missing obs
						return({"case_id":case_id,"ltvs":ltvs,"ages":ages,"terminations":terminations})
					except ValueError:
						pass

	data_terminate = []
	data_ltv = []
	data_age = []
	data_case_id = []

	NTHREAD = 5
	if __name__ == '__main__':
		with Pool(NTHREAD) as u:
			k = u.map(do_term,[i for i in set(df.case_id)])

	for i in k:
		try:
			for j in range(len(i["ages"])):
				print(j,i["ltvs"][j])
				data_case_id.append(i["case_id"][j])
				data_age.append(i["ages"][j])
				data_ltv.append(i["ltvs"][j])
				data_terminate.append(i["terminations"][j])
			print(i)
			print(data_ltv)
		except TypeError:
			pass
			

dd = pd.DataFrame([data_case_id,data_ltv,data_age,data_terminate]).T
print(dd.describe())
dd.columns = ["case_id","ltv","age","terminate"]
print(dd.describe())
print(data_ltv)
print(data_terminate)
print(data_age)

plt.scatter(dd.ltv,dd.terminate)
plt.savefig("dummy.png")

dd.to_csv("dummy.csv")

	
