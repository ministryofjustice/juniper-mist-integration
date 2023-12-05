#!/bin/bash

if [ "$RUN_UNIT_TESTS" = True ] ; then
  python -m unittest discover -s /app -t /app
else
  python /app/src/main.py
fi
