# calsync
Calendar synchronization client.
Works with Google Calendar, Exchange and ical files.

## Installation

Prerequisites:
* [Python3](https://www.python.org/downloads/)
* [pip](https://pypi.python.org/pypi/pip)

Dependecies :
* [icalendar](https://github.com/collective/icalendar.git)
* [exchangelib](https://pypi.python.org/pypi/exchangelib)
* [google-api-python-client](https://developers.google.com/api-client-library/python/)
* [simple-crypt](https://pypi.python.org/pypi/simple-crypt)

If you want to create a vitrualenv for the project :
> `pip install virtualenv`  
> `sudo virtualenv -p python3 venv`  
> `source venv/bin/activate`

Then, to install all requirements : 
> `pip install -r requirements.txt`  

If you have issues installing simple-crypt, try :
> `apt-get install python3-dev`  

## Run

> `python calsync.py \<configuration_file>`  

for more informations on arguments :
> `python calsync.py --help`  

## Edit configuration file

Configuration is strored in a JSON file. You can difine your calendars and several rules to apply for the synchronization.

In this simple example, you will define a Google and an Exchange calendar. The rule tells calsync to add all events from Exchange to Google.
```json
  "definitions":{
    "G":{
      "type":"google",
      "id":"<primary|calendar id>"
    },
    "E":{
      "type":"exchange",
      "server":"<exchange server>",
      "username":"<DOMAIN>\\<username>",
      "address":"<email address>"
    }
  },
  "rules":[
    {
      "operation": "union",
      "operands": ["E"],
      "destination": "G"
    }
  ]
}
```

You can find config examples in the `configurations` directory.
