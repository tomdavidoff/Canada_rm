# clean_mortality.py
# make clean mortality
# Tom Davidoff
# 08/17/20

g = open("Documents/rmfix/data/mortality_female_clean_canada.csv","w")
g.write("age,mortality\n")
f = open("Documents/rmfix/data/mortality_female_statcan.csv","r")
for line in f:
	if "years" in line and '"' in line:
		age = line.replace('"','').split(' ')[0]
		mortality = line.replace('"','').strip().split(",")[1]
		if len(line.split(","))==2:
			g.write(age+","+mortality+"\n")
