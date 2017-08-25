pi-netwatch
=====

regularly ping common public servers. Keep a log of success or failure. Periodically send an email report describing the connectivity situation.

to run:

`python netwatch.py`

and it will send reports every seven days

`python netwatch.py logfile_name`

will send a report based on `logfile_name` immediately
