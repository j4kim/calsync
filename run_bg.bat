@ECHO OFF
ECHO Calsync is running in background, you can close this window
ECHO To stop Calsync, use your system task manager and kill Python instances
pythonw ./src/calsync.py ./calsync.conf.json
pause