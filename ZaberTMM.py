#!/usr/bin/python3 -u
from tango.server import run
import os
from ZaberTMMAxis import ZaberTMMAxis
from ZaberTMMCtrl import ZaberTMMCtrl

# Run ZaberTMMCtrl and ZaberTMMAxis
run([ZaberTMMCtrl, ZaberTMMAxis])