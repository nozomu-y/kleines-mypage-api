#!/usr/local/bin/python3
# -*- coding: UTF-8 -*-

from wsgiref.handlers import CGIHandler
from app import app
import cgitb
cgitb.enable()

CGIHandler().run(app)
