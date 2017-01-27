#!/bin/bash
echo "Calsync is running in background, you can close this window"
echo "To stop Calsync, use your system task manager and kill Python instances"
pythonw ./src/calsync.py ./calsync.conf.json
read