#! /bin/bash
sleep 5
s=`/usr/bin/curl http://ipv4.icanhazip.com`
echo `hostname` IPV4 $s
echo $s | mail -s "IPV4 for `hostname` `/bin/date`" bjorke@botzilla.com
