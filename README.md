# calsync
Calendar synchronization client.
Works with Google Calendar, Exchange and ical files.

## Installation

Prerequisites:
* [Python3](https://www.python.org/downloads/)
* [pip](https://pypi.python.org/pypi/pip) (auto installed if you use venv)

Dependecies :
* [icalendar](https://github.com/collective/icalendar.git)
* [exchangelib](https://pypi.python.org/pypi/exchangelib)
* [google-api-python-client](https://developers.google.com/api-client-library/python/)
* [simple-crypt](https://pypi.python.org/pypi/simple-crypt)


First, be sure to use python 3 :  

> `python --version`  

If you don't see `Python 3.x.y`, You can either :  
* Intall Python 3 if you don't have it
* Use `python3` instead of `python`
* Create an alias like : `alias python=python3`

Now you need to install dependencies.  
I recommand to create a virtual environment to avoid packages versions conflicts.  
In the project directory, run :  
> `python -m venv venv`  

Then activate the venv :  
> `source venv/bin/activate` (Linux/Mac OS)   
> `venv\Scripts\activate.bat` (Windows)  

Then, to install all requirements : 
> `pip install -r requirements.txt` (prefix with `sudo` or run as admin if needed)

## Edit configuration file

Configuration is strored in a JSON file. You can difine your calendars and several rules to apply for the synchronization.

In this example, we will define two Google, one Exchange and one ICS calendar.  
The first rule tells calsync to add all events from both "perso" and "work" calendars to "common".  
Then, the second rule will make a copy of all events in "common" into a local ics file.

```json
  "definitions":{
    "perso":{
      "type":"google",
      "id":"primary"
    },
    "common":{
      "type":"google",
      "id":"3mnnljsfhcu14k8n398h9o4oh8@group.calendar.google.com"
    },
    "work":{
      "type":"exchange",
      "server":"domain.server.com",
      "username":"DOMAIN\\user.name",
      "address":"user.name@server.com"
    },
    "localcopy":{
      "type":"ics",
      "path":"out.ics"
    }
  },
  "rules":[
    {
      "operation": "union",
      "operands": ["work", "perso"],
      "destination": "common"
    },
    {
      "operation": "union",
      "operands": ["common"],
      "destination": "localcopy"
    }
  ]
}
```

### Anonymous events  

In a rule, you can add a custom "subject" entry. That will tell Calsync to override all events name by the subject given.  
Example :
```json
    "rules":[{
      "operation": "union",
      "operands": ["personnal"],
      "destination": "common",
      "subject": "Joaquim is busy"
    }]
```

### About Google Calendars

Google calendars are referenced by a Google-specific id, you can find this id in your calendar's settings.  
The keyword "primary" references the default calendar of the Google Account. You can't use several Google Accounts, but you can share calendars between accounts that need to sync.  
If you want to switch account, just remove the generated directory `~/.credentials`, in your user home folder. 

## Run

> `python src/calsync.py calsync.conf.json`  

For more informations on arguments :
> `python src/calsync.py --help`

You can also use `run.sh` or `run.bat` for quick run.
