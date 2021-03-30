#! /bin/bash
curl http://ipv4.icanhazip.com | mail -s "IPV4 for `hostname` now" bjorke@botzilla.com
