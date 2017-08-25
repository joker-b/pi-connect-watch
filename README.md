pi-netwatch
=====

regularly ping common public servers. Keep a log of success or failure. Periodically send an email report describing the connectivity situation.

to run:

`python netwatch.py`

and it will send reports every seven days.

On pi2's you may need to use `sudo`:

`sudo python netwatch.py`

Running the command will give you a hint if this is needed

Immediate Report
==

`python netwatch.py _logfile_name_`

will send a report based on `_logfile_name_` immediately.

Or 

`python netwatch.py now`

to use the default logfile name, with a report named "now"

Suggested Pi Usage
==

put this into `rc.local` to start reporting on reboot for a typical pi:

```
python /home/pi/src/pi-connect-watch reboot
python /home/pi/src/pi-connect-watch &
```



