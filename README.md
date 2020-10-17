# brownpaperbag

[![PyPI - version](https://img.shields.io/pypi/v/brownpaperbag.svg)](https://pypi.python.org/pypi/brownpaperbag)
![](https://github.com/bpaulin/brownpaperbag/workflows/build/badge.svg)
[![CodeFactor](https://www.codefactor.io/repository/github/bpaulin/brownpaperbag/badge)](https://www.codefactor.io/repository/github/bpaulin/brownpaperbag)
[![codecov](https://codecov.io/gh/bpaulin/brownpaperbag/branch/master/graph/badge.svg)](https://codecov.io/gh/bpaulin/brownpaperbag)

> But you try and tell the young people today that...

## installation

``` {.sourceCode .bash}
pip install brownpaperbag
```

## Configuration

You need to use the official app, and to be logged with the installer code

You'll need the open password: From the app, you can set it on Other\>System. You'll also need your gateway's IP: Again from the app, you can find it in Other\>Network

So if your ip is 192.168.1.10 and your password is qwerty:

``` {.sourceCode .bash}
export BPB_HOST=192.168.1.10
export BPB_PASSWORD=qwerty
export BPB_PORT=20000
```

## Commands

``` {.sourceCode .bash}
brownpaperbag --help
Usage: brownpaperbag [OPTIONS] COMMAND [ARGS]...

  Console script for brownpaperbag.

  Provides interaction with myhomeserver1

Options:
  --host TEXT      MyHomeServer1 IP
  --port INTEGER   MyHomeServer1 port
  --password TEXT  OPEN password
  -v, --verbose    Verbose mode, can be used twice
  --help           Show this message and exit.

Commands:
  cover  Interact with a cover.
  event  Subscribe to gateway events.
  light  Interact with a light.
  list   List known devices.
  raw    Send raw openwebnet command.
```

### Cover interaction

``` {.sourceCode .bash}
Usage: brownpaperbag cover [OPTIONS] COVER_ID

  Interact with a cover.

Options:
  --status  Get status
  --up      Open
  --down    Close
  --stop    Stop
  --help    Show this message and exit.
```

### Listen to events

``` {.sourceCode .bash}
Usage: brownpaperbag event [OPTIONS]

  Subscribe to gateway events.

Options:
  --human  Human readable
  --help   Show this message and exit.
```

### Light interaction

``` {.sourceCode .bash}
Usage: brownpaperbag light [OPTIONS] ID

  Interact with a light.

Options:
  --status  Get status
  --on      Turn On
  --off     Turn Off
  --help    Show this message and exit.
```

### List every devices

``` {.sourceCode .bash}
Usage: brownpaperbag list [OPTIONS]

  List known devices.

Options:
  --lights / --no-lights  Include lights
  --covers / --no-covers  Include covers
  --help                  Show this message and exit.
```

### Send raw command

``` {.sourceCode .bash}
Usage: brownpaperbag raw [OPTIONS] COMMAND

  Send raw openwebnet command.

Options:
  --help  Show this message and exit.
```

## Help & tricks

### Discovering devices

the command `brownpaperbag event --human` can help you to identify devices

``` {.sourceCode .bash}
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
```
