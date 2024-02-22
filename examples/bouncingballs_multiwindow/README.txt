Bouncing balls example.

Adopted from what seems to be the most up-to-date version of this example:
  https://msdl.uantwerpen.be/git/simon/SCCD/src/master/examples/bouncingballs/python/sccd_multiwindow.xml

To (re-)compile:
  Dependencies:
    Python 3
    SCCD2DEVS must be in your PYTHONPATH environment variable.
  Run:
    python3 -m sccd.compiler.sccdc sccd_multiwindow.xml -p eventloop

To run the example:
  Dependencies:
    Python 3 and TkInter
  Run:
    python3 runner_multiwindow.py
