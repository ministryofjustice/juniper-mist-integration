#!/bin/bash

if [ "$RUN_UNIT_TESTS" = True ] ; then
  python -m unittest discover -s /app/src_backend -t /app
else
  cd /app/src_frontend/src/ && flask --app app run --host=0.0.0.0
fi
