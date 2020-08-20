# canada.py
# python to make stuff
# Tom Davidoff
# 03/31/20

# import libraries
import pandas as pd
import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
import math
import matplotlib.pyplot as plt
from linearmodels.iv import IV2SLS
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.iolib.summary2 import summary_col
from matplotlib.backends.backend_pdf import PdfPages
from multiprocessing import Pool	

# DISCOUNT RATE?
CPI = .02
DISCOUNT = .015 # current?
ADMIN = .21 # see if less crazy -- no multiplying by 2 makes little difference Genworth quarterly statements

# EXTRA COST OF DEFAULT -- this is in the default probability multiplier

# graph for proposal
age = range(75,110)
ageo = 75
rate = .05
ghigh = .03
glow = .01
ltv0 = .5
LTVhigh = [ltv0*((1+rate)/(1+ghigh))**(i-75) for i in age]
LTVlow = [ltv0*((1+rate)/(1+glow))**(i-75) for i in age]

plt.scatter(age,LTVhigh)
plt.scatter(age,LTVlow)
plt.xlabel("Borrower age ")
plt.ylabel("mark-to-market LTV")
plt.legend(['3% growth','1% growth'])
plt.savefig("Documents/rmfix/text/ltv.png")
plt.close()

# Get parameters
# default value = prob(default)*loss given default
# See HOME partnership paper
# translating from the R

r = .025 # current rate
amort = 300
rm = (1+r)**(2/12)-1 # monthly rate
print(rm)
pmt = rm/(1-(1+rm)**(-amort))
print(pmt)
t = np.arange(1,11) # year end balance -- may understate year 5 exit
osb = np.array([(pmt/rm)*(1-(1+rm)**(-amort+12*tau)) for tau in t])
ltv_points = [.8,.85,.9,.95]
ltv_stats = {v:{"osb":v*osb} for v in ltv_points}
print(ltv_stats)
prepay = 0.001865*t*12+0.008135 # per https://iiac.ca/wp-content/uploads/IIAC-MBS-Committee-NHA-MBS-Linear-Liquidation-Model-v-1.1.pdf
# random assumption here
prepay[5-1] = .5
print("prepay",prepay)

# first and second moment of truncated lognormal
def e1(mu,sigma,a):
	a0 = (np.log(a)-mu)/sigma
	return(np.exp(mu+sigma*sigma/2)*norm.cdf(-sigma+a0)/norm.cdf(a0))

def e2(mu,sigma,a) :
	a0 = (np.log(a)-mu)/sigma
	return(np.exp(2*mu+2*sigma*sigma)*norm.cdf(-2*sigma+a0)/norm.cdf(a0))

def loss(mu,sigma,a) : # dollars lost need to scale!
	return(norm.cdf(np.log(a),mu,sigma)*(1-2*e1(mu,sigma,a)/a + e2(mu,sigma,a)/(a*a) ))

# verify these are correct
m = .01
s = .01
aa = math.exp(m+s+s)
print(e1(m,s,aa))
print(e2(m,s,aa))
r = np.random.lognormal(m,s,100000)
print(np.mean(r[r<aa]))
print(np.mean((r*r)[r<aa]))

# loss function per the text
L = .95
ll = np.mean((L>r)*(L-r)*(L-r)/(L*L))
print(ll)
print(e1(m,s,L))
print(e2(m,s,L))
print(norm.cdf(np.log(L),m,s))
print(loss(m,s,L))
print("it works!")


#price targets
#Loan-to-Value 	Premium on Total Loan 	Premium on Increase to Loan Amount for Portability
#Up to and including 65% 	0.60% 	0.60%
#Up to and including 75% 	1.70% 	5.90%
#Up to and including 80% 	2.40% 	6.05%
ltv_stats[.8]["fee"] = .024*.8
#Up to and including 85% 	2.80% 	6.20%
ltv_stats[.85]["fee"] = .028*.85
#Up to and including 90% 	3.10% 	6.25%
ltv_stats[.9]["fee"] = .031*.9
#Up to and including 95% 	4.00% 	6.30%
ltv_stats[.95]["fee"] = .04*.95
#90.01% to 95% —
#Non-Traditional Down Payment** 	4.50% 	6.60 %


def misprice(x):
	#m = x[0]
	m = 0
	#s = x[1]
	s = x
	for v in ltv_stats:
		ltv_stats[v]["cost"]= ADMIN*ltv_stats[v]["fee"] # per Genworth cost of administration?
		ltv_stats[v]["survival"]=1
		for tau in t:
			ltv_stats[v]["cost"] = ltv_stats[v]["cost"] + loss(m*tau,s,ltv_stats[v]["osb"][tau-1])*ltv_stats[v]["survival"]*(1+DISCOUNT)**(-tau) # note s time-varying meh
			ltv_stats[v]["survival"]=ltv_stats[v]["survival"]*(1-prepay[tau-1])

	delta = sum([(ltv_stats[v]["cost"]-ltv_stats[v]["fee"])*(ltv_stats[v]["cost"]-ltv_stats[v]["fee"]) for v in ltv_stats])
	return(delta)

p = minimize(misprice,.05)
print(p)
print(p["x"])
for k in range(1,30):
	print(["LOSS!",k,misprice(k*.01),np.sqrt(misprice(k*.01))])
print(loss(0,.3,.85))
print(loss(0,.3,.9))
print(loss(-.02,.3,.95))
print(ltv_stats)


# A bit of mobility
mobility = {j:{i:{"Canada":0,"BC":0} for i in [1,5]} for j in [70,75,80,85]}
mobility[70][1]["Canada"] = (70985-4260)/(1383845-4260)
mobility[75][1]["Canada"] = (46640-2810)/( 968540-2810)
mobility[80][1]["Canada"] = ( 30685 -  1380 )/(661710 - 1380)
mobility[85][1]["Canada"] = (22795 - 685)/( 522395 - 685)
mobility[70][1]["BC"] = (13085-845)/(198715-845)
mobility[75][1]["BC"] = (8635-545)/( 139995-545)
mobility[80][1]["BC"] = ( 5540 - 310) / (96370-310)
mobility[85][1]["BC"] = (3830 - 145)/(77750-145)
mobility[70][5]["Canada"] = ( 249420 -15660)/(1383845-15660)
mobility[75][5]["Canada"] = ( 161515 -9955)/( 968540-9955)
mobility[80][5]["Canada"] = ( 105075 -  4380 )/(661710 - 4380)
mobility[85][5]["Canada"] = (78730 - 1910)/( 522400 - 1910)
mobility[70][5]["BC"] = (44435-3115)/(198715-3115)
mobility[75][5]["BC"] = (28030-2045)/( 139995-2045)
mobility[80][5]["BC"] = ( 17960 - 905) / (96370-905)
mobility[85][5]["BC"] = (12730 - 380)/(77750-380)

for i in mobility:
	print([i,mobility[i][1]["Canada"],mobility[i][1]["BC"],mobility[i][5]["Canada"],mobility[i][5]["BC"]])
	print([i,mobility[i][1]["Canada"]/mobility[i][1]["BC"],mobility[i][5]["Canada"]/mobility[i][5]["BC"]])
	print([i,mobility[i][1]["Canada"]/mobility[i][5]["Canada"],mobility[i][1]["BC"]/mobility[i][5]["BC"]])

mobility_11 = {j:{i:{"Canada":0,"BC":0} for i in [1,5]} for j in [75]}
mobility_11[75][1]["Canada"] = (84410-2905)/(1927000-2905)
mobility_11[75][1]["BC"] = (13505-670)/(278850-670)
mobility_11[75][5]["Canada"] = (315215-9955)/(1927000-9955)
mobility_11[75][5]["BC"] = (50750-2115)/(278850-2115)

print(mobility_11)

#conclusion: there is some differential uptick
# endogenous makes sense for general pop -- also see Vancouver excess std dev

#Looks like price is double risk

mortality = {}
with open("Documents/rmfix/data/survival_statcan.csv","r") as fl:	
	for line in fl:
		l = line.strip().replace('"','').split(",")
		if "years" in l[0]:
			lage = int(l[0].split(' ')[0])
			survival = float(l[len(l)-1])
			mortality[lage] = 1-survival


mortality_male = {}
with open("Documents/rmfix/data/statscan_male_mortality.csv","r") as fm:
	for line in fm:
		l = line.strip().replace('"','').split(",")
		if "years" in l[0]:
			lage = int(l[0].split(' ')[0])
			mortality_male[lage] = float(l[1])
	

print("MORTALITY")
print(mortality)
print(mortality_male)

# pseudo code for profit

# integrate over mortality possibilities
# draw many price paths
# here is a price path
chip_terms = {75:{"chip":.43,"chip_max":.5},70:{"chip":.383,"chip_max":.454},65:{"chip":.3575,"chip_max":.4275},78:{"chip":.5,"chip_max":.55}}
min_age = 65
BASELINE_EQUITY = .5 # I think Davidoff Welke basically .5
MAX_AGE = 109
STD_DEV_MKT = .065  # half to market -- .05 difference across all CDN metros -- not at all scaling Greater Vancouver per CRE
STD_DEV_INDIV = .10 # half of 30 to individual, make persistent
# SUNLIFE .073751 age 75
# What is fair?
print("LOAD")
min_age=75
survival= {}
survival[min_age]=1
ages = range(min_age+1,MAX_AGE+1) # dead at 111 for sure
print(ages)
DISCOUNT_QUOTE = .0025 # current
for age in ages:
	survival[age] = survival[age-1]*(1-mortality[age-1]) 

cost = sum([(1*(i<86) + (i>85)*survival[i])*(1+DISCOUNT_QUOTE)**(-i) for i in range(76,110)]) # 10 year guarantee!
print(["FOR WOMEN",cost,1/cost])

print("LOAD men")
min_age=75
survival= {}
survival[min_age]=1
ages = range(min_age+1,MAX_AGE+1) # dead at 111 for sure
print(ages)
for age in ages:
	survival[age] = survival[age-1]*(1-mortality_male[age-1]) 

cost = sum([(1*(i<86) + (i>85)*survival[i])*(1+DISCOUNT)**(-i) for i in range(76,110)]) # 10 year guarantee!
print(["FOR MEN",cost,1/cost])




LOAD = 0*.15 # women get better pricing unisex
TINY = .00001
MOVE_ALIVE_SENSITIVITY = .1  # Moral hazard measure from Davidoff Welke but Canadianize -- about 1% different BC vs Canada 2016, call it extra 2 for 20
ANNUITY_SENSITIVITY = 1 # how does annuity PV compare to equity as motivator to move
TERM_PREMIUM = .005
CONSTANT_MOVE = .03
HECM_SPREAD = .025 # 10 year CMHC insured loans in Canada, consistent with HECM adjustable
#loan = .5 # for starters -- close to CHIP


discounts = [.01,.03]
annuity_fracs = [0,.1,.25,.4,.5]
min_ages = [65,70,78]
products = ["chip_max"]
scenarios = {d:{f:{m:{p:0 for p in products} for m in min_ages} for f in annuity_fracs} for d in discounts}
for DISCOUNT in discounts:
	for product in products:
		for min_age in min_ages:
			for ANNUITY_FRAC in annuity_fracs: 
				loan = chip_terms[min_age][product]
				rate = DISCOUNT + HECM_SPREAD # rationale: spread on 10 year CMHC insured product = 2.5%, add in a term premium. Not far from current (risky) CHIP Price  #.0399 less HECM insure annual of .25%?
				rate_max = rate # not clear should do with insurance! a
				loan_rate = rate
				survival= {}
				survival_male = {}
				survival[min_age]=1
				survival_male[min_age]=1
				ages = range(min_age+1,MAX_AGE+1) # dead at 111 for sure
				for age in ages:
					survival[age] = survival[age-1]*(1-mortality[age-1]) 
					survival_male[age] = survival_male[age-1]*(1-mortality_male[age-1]) 
				prob_husband = {}
				prob_wife = {}
				prob_couple = {}
				death_prob = {min_age:mortality[min_age]*mortality_male[min_age]}
				survival_joint_life = {min_age:1}
				prob_couple[min_age]=1
				prob_husband[min_age]=0
				prob_wife[min_age]=0
				for age in ages:
					prob_couple[age]=prob_couple[age-1]*(1-mortality[age-1])*(1-mortality_male[age-1])
					prob_husband[age] = prob_husband[age-1]*(1-mortality_male[age-1]) +prob_couple[age-1]*mortality[age-1]*(1-mortality_male[age-1])
					prob_wife[age] = prob_wife[age-1]*(1-mortality[age-1]) +prob_couple[age-1]*mortality_male[age-1]*(1-mortality[age-1])
					survival_joint_life[age] = prob_couple[age]+prob_husband[age]+prob_wife[age]
					if survival_joint_life[age]>1:
						print("SURVIVAL ERROR!",age)
				mortality[MAX_AGE] = 1-TINY
				for age in ages:
					death_prob[age] = prob_couple[age]*mortality_male[age]*mortality[age] + prob_husband[age]*mortality_male[age] + prob_wife[age]*mortality[age]

				annuity_amount = (1-loan)*ANNUITY_FRAC # just for now
				borrower_discount = rate
				annuity_value = {}
				annuity_cost = sum([survival[age]*(1+DISCOUNT)**(min_age-age) for age in ages])*(1+LOAD)
				annuity_cash = annuity_amount/annuity_cost
				for age in ages:
					annuity_value[age] = annuity_cash*sum([(survival_joint_life[i]/survival_joint_life[age])*(1+borrower_discount)**(age-i) for i in range(age,MAX_AGE)])
				balance = {}
				balance[min_age] = loan+annuity_amount
				for age in ages:
					balance[age] = balance[age-1]*(1+loan_rate)-annuity_cash
				# assume borrower discounts at rate plus spread by revealed preference?
				lender_discount = DISCOUNT + TERM_PREMIUM

				def move_prob(age,equity):
					return(CONSTANT_MOVE+MOVE_ALIVE_SENSITIVITY*(equity+ANNUITY_SENSITIVITY*annuity_value[age]))

				def valuation(loop=0):
					market = np.random.normal(loc=CPI,scale = STD_DEV_MKT,size=len(ages))
					idiosyncratic = np.random.normal(loc=0,scale=STD_DEV_INDIV)
					value = np.exp(np.cumsum(market)+idiosyncratic)
					random_move = np.random.random(len(ages))
					fee = .00
					profit = fee-loan  # assume no death until anniversary if terminate immediately
					sterminate = 0
					still_there = 1
					gone_alive = 0
					insurance_cost = 0
					for age in ages:
						leave_alive = (1-death_prob[age])*move_prob(age,max(value[age-min_age-1]-balance[age],0))
						if move_prob(age,max(value[age-min_age-1]-balance[age],0))<0:
							print("ERROR SUB ZERO",min_age)
						if move_prob(age,max(value[age-min_age-1]-balance[age],0))>1:
							print("ERROR ONE PLUS") # just at one period before death
						terminate_probability = still_there*(1-gone_alive)*(death_prob[age]+leave_alive)
						profit+=terminate_probability*(1+lender_discount)**(min_age-age)*min(balance[age],value[age-min_age-1])
						insurance_cost += (1+lender_discount)**(min_age-age)*terminate_probability*max(0,balance[age]-value[age-min_age-1])
						sterminate += terminate_probability
						gone_alive += leave_alive*survival[age]*(1-gone_alive)
						still_there = still_there-terminate_probability
					return(insurance_cost)

				profits = []

				NTHREAD = 5
				if __name__ == '__main__':
					with Pool(NTHREAD) as u:
						k = u.map(valuation,[i for i in range(100000)])


				for i in k:
					profits.append(i)

				#print([max(profits),min(profits),np.mean(profits),np.mean(np.array(profits)<0)])
				print([product,DISCOUNT,ANNUITY_FRAC,min_age,round(np.mean(profits),4)])
				scenarios[DISCOUNT][ANNUITY_FRAC][min_age][product] = np.mean(profits)

df = pd.DataFrame.from_dict(scenarios)
print(df)
