# hecm_terminate.R
# R to analyze
# Tom Davidoff
# 08/17/20

a <- read.csv("Documents/rmfix/data/mortality_female_clean_canada.csv")
b <- read.csv("Documents/rmfix/data/hecm_results.csv")

summary(b)
for (n in names(b)) {
	b[[n]] <- as.numeric(b[[n]])
}

summary(a)
summary(b)

a <- merge(a,b)
# mortality <- (1-x)^12 = 1-m
# (1-m)^(1/12) = 1-x
# x 
a$mortality <- 1- (1-a$mortality)^(1/12)

a$min_year <- ave(a$year,a$case_id,FUN=min)
a$fltv <- ave(a$ltv*(a$year==a$min_year),a$case_id,FUN=max)
a$time <- a$year-a$min_year

summary(lm(a$terminate ~ 0 + a$mortality + factor(a$time) + factor(round(a$ltv*10))))
summary(lm(a$terminate ~ 0 + a$mortality + factor(a$time) + a$ltv))
summary(lm(a$terminate ~ 0 + a$mortality + factor(a$time) + a$ltv,subset=a$ltv<1))
summary(lm(a$terminate ~ 0 + a$mortality + factor(a$time) + a$ltv,subset=a$ltv<a$fltv))


