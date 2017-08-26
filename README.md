# pi-netwatch

regularly ping common public servers. Keep a log of success or failure. Periodically send an email report describing the connectivity situation.

to run:

`python netwatch.py`

and it will send reports every seven days.

On pi2's you may need to use `sudo`:

`sudo python netwatch.py`

Running the command will give you a hint if this is needed

## Immediate Reporting

Netwatch.py will generate report emails every few days. If you're impatient, try

`python netwatch.py now`

to use the default logfile name, with a report named "now"

to use a specific logfile name, use the logfile instead of the report name, e.g.

`python netwatch.py _logfile_name_`

## Suggested Pi Automated Usage

put this into `rc.local` to start reporting on reboot for a typical pi:

```
python /home/pi/src/pi-connect-watch/netwatch.py &
```



