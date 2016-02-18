c<-read.table('gpsPPS0.dat')
summary(c)
nrecords<-nrow(c)
c<-head(c,nrecords-1)
f<-head(c$V1,1)
s <- seq(f,f+nrecords,by=1.)  
s
d<-c-s
plot(d$V1*1000000,ylab='microseconds',col='green',main='TimeStamp error (absolute)')
hist(d$V1*1000000,breaks=20,xlab='microseconds',col='green',main='TimeStamp error (absolute)')

