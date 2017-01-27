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

## Run

> `python calsync.py <configuration_file>`  

for more informations on arguments :
> `python calsync.py --help`  

## Edit configuration file

Configuration is strored in a JSON file. You can difine your calendars and several rules to apply for the synchronization.

In this simple example, we will define two Google and one Exchange calendar. The rule tells calsync to add all events from both "perso" and "work" calendars to "common".
```json
  "definitions":{
    "perso":{
      "type":"google",
      "id":"primary"
    },
    "common":{
      "type":"google",
      "id":"3mnnljsfhcu14k8n398h9o4oh8@group.calendar.google.com"
    }
    "work":{
      "type":"exchange",
      "server":"domain.server.com",
      "username":"DOMAIN\\user.name",
      "address":"user.name@server.com"
    }
  },
  "rules":[
    {
      "operation": "union",
      "operands": ["work", "perso"],
      "destination": "common"
    }
  ]
}
```

