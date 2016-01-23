c<-read.table('client.dat')
s<-read.table('server.dat')
nrecords<-min(nrow(s),nrow(c))-1
c<-head(c,nrecords)
s<-head(s,nrecords)

d<-c-s
f<-head(d,1)
l<-tail(d,1)
p<-l-f
n<-nrow(s)
i<-(tail(c,1)-head(c,1))
tdelta<-i/n
t<-(nrow(d)*tdelta)
ppm<-p*1000000/t
summary(d)
plot(d$V1*1000000,ylab='microseconds',col='green',main='TimeStamp error (absolute)')
hist(d$V1*1000000,breaks=20,xlab='microseconds',col='green',main='TimeStamp error (absolute)')
offset<-mean(d$V1)
dd<-d-offset
plot(dd$V1*1000000,main='TimeStamp error (corrected)',ylab='microseconds',col='blue')

hist(dd$V1*1000000,breaks=20,xlab='microseconds',col='blue',main='TimeStamp error (corrected)')

n
i
tdelta
ppm
ppmOS=(i-n)*1000000/n
ppmOS
