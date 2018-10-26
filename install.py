#!/usr/bin/env python
import sys
import subprocess
from os.path import expanduser

subprocess.call(["sudo","mkdir","/usr/share/secretflyingpush"])
subprocess.call(["sudo","cp", "res","-r","/usr/share/secretflyingpush"])
subprocess.call(["sudo","cp", "src","-r","/usr/share/secretflyingpush"])
subprocess.call(["sudo","chmod","777","/usr/share/secretflyingpush/src"])

if len(sys.argv) > 1:
    if sys.argv[1] == "all":
        subprocess.call(["pip","install","geotext"])
        subprocess.call(["pip","install","notify2"])
        subprocess.call(["sudo","apt-get","install","python-pyaudio"])
print "Install complete"
print "You can now remove this directory"
