#! /bin/bash
sleep 2m
/usr/bin/curl http://ipv4.icanhazip.com | mail -s "IPV4 for `hostname` `/bin/date`" bjorke@botzilla.com
