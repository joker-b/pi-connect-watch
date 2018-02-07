# pi-netwatch

A small Raspberry Pi program to monitor home network connectivity to the internet, and to monitor the local and possibly-dynamic IP address (handy if you want to use SSH etc). Could work on other systems, I used a pi. The pi needs to have emailing enabled, and chnage the email address in this repo or your copy will send mail to me rather than you.

Regularly ping common public servers. Keep a log of success or failure. Periodically send an email report describing the connectivity situation.

Each time a report is sent, the email will also contain the current IPv4 and IPv6 addresses of the pi.

To run (pthon2 btw):

`python netwatch.py`

and it will send reports every seven days.

On pi2's you may need to use `sudo`:

`sudo python netwatch.py`

Running the command will give you a hint if this is needed

## Immediate Reporting

Netwatch.py will generate report emails every few days. If you're impatient, try

`python netwatch.py now`

to use the default logfile name, with a report named "now" (and as usual contianing the machine's current IP addresses).

to use a specific logfile name, use the logfile instead of the report name, e.g.

`python netwatch.py _logfile_name_`

## Suggested Pi Automated Usage

put this into `/etc/rc.local` to start reporting on reboot for a typical pi:

```
python /home/pi/src/pi-connect-watch/netwatch.py &
```



