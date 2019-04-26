brownpaperbag
=============

|image| |GitHub| |PyPI - Downloads|

|image| |Updates|

   But you try and tell the young people today that...

installation
------------

.. code:: bash

   pip install brownpaperbag

Usage (cli)
-----------

Configuration
~~~~~~~~~~~~~

You need to use the official app, and to be logged with the installer
code

You'll need the open password: From the app, you can set it on
Other>System. You'll also need your gateway's IP: Again from the app,
you can find it in Other>Network

So if your ip is 192.168.1.10 and your password is qwerty:

.. code:: bash

   export BPB_HOST=192.168.1.10
   export BPB_PASSWORD=qwerty
   export BPB_PORT=20000

Discovering devices
~~~~~~~~~~~~~~~~~~~

the command ``brownpaperbag event --human`` can help you to discover
devices

.. code:: bash

   $ brownpaperbag event --human
   light 15 is OFF (*1*0*15##)
   light 11 is OFF (*1*0*11##)
   light 0010 is OFF (*1*0*0010##)
   light 0011 is OFF (*1*0*0011##)
   light 0012 is OFF (*1*0*0012##)
   light 02 is OFF (*1*0*02##)
   light 0014 is OFF (*1*0*0014##)
   light 0111 is OFF (*1*0*0111##)
   light 04 is OFF (*1*0*04##)
   light 19 is OFF (*1*0*19##)
   light 01 is OFF (*1*0*01##)
   light 09 is OFF (*1*0*09##)
   cover 07 is STOPPED (*2*0*07##)
   cover 0113 is STOPPED (*2*0*0113##)
   cover 13 is STOPPED (*2*0*13##)
   cover 17 is STOPPED (*2*0*17##)
   cover 16 is STOPPED (*2*0*16##)
   cover 06 is STOPPED (*2*0*06##)
   cover 08 is STOPPED (*2*0*08##)
   cover 06 is UP (*2*1000#1*06##)
   cover 06 is STOPPED (*2*1000#0*06##)
   cover 06 is DOWN (*2*1000#2*06##)
   cover 06 is STOPPED (*2*1000#0*06##)
   light 0111 is ON (*1*1*0111##)
   light 0111 is OFF (*1*0*0111##)
   light 0111 is ON (*1*1*0111##)
   light 0111 is OFF (*1*0*0111##)
   cover 06 is DOWN (*2*1000#2*06##)
   cover 06 is STOPPED (*2*1000#0*06##)
   cover 06 is UP (*2*1000#1*06##)
   cover 06 is STOPPED (*2*0*06##)

.. |image| image:: https://img.shields.io/pypi/v/brownpaperbag.svg
   :target: https://pypi.python.org/pypi/brownpaperbag
.. |GitHub| image:: https://img.shields.io/github/license/bpaulin/brownpaperbag.svg
.. |PyPI - Downloads| image:: https://img.shields.io/pypi/dm/brownpaperbag.svg
.. |image| image:: https://img.shields.io/travis/bpaulin/brownpaperbag.svg
   :target: https://travis-ci.org/bpaulin/brownpaperbag
.. |Updates| image:: https://pyup.io/repos/github/bpaulin/brownpaperbag/shield.svg
   :target: https://pyup.io/repos/github/bpaulin/brownpaperbag/
