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

`python netwatch.py logfile_name`

will send a report based on `logfile_name` immediately
