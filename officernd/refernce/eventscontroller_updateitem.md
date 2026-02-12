# Update an existing event.

Source: https://developer.officernd.com/reference/eventscontroller_updateitem

eventId

string

required

Id of the event.

orgSlug

string

required

organization slug

Event data to update.

title

string

The title of the event.

where

string

A description of where the event will be taking place.

# `` 200

object

\_id

string

The \_id of the event.

start

string

The start date of the event.

end

string

The end date of the event.

timezone

string

The timezone of the event.

title

string

The title of the event.

location

string

The \_id of the location of the event.

locations

array of strings

The ids of the locations where the event is visible.

locations

description

string

The description of the event.

where

string

A description of where the event will be taking place.

company

string

The \_id of the company that will be associated with the event.

member

string

The \_id of the member who created the event.

limit

number

The number of participants that this event will host.

links

array of strings

An array containing all the links associated with the events.

links

image

string

The image link associated with the event.

Updated 5 months ago

* * *

Did this page help you?

Yes

No

ShellNodeRubyPHPPython

Bearer

```

xxxxxxxxxx

curl --request PUT \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/events/eventId \

     --header 'accept: application/json' \

     --header 'content-type: application/json'
```

```

xxxxxxxxxx



{

  "_id": "603dfbc260f4054084125d30",

  "start": "2024-01-01T06:00:00Z",

  "end": "2024-01-01T12:00:00Z",

  "timezone": "America/New_York",

  "title": "Lunch and Learn",

  "location": "603dfbc260f4054084125d33",

  "locations": [\
\
    "603dfbc260f4054084125d33",\
\
    "603dfbc260f4054084125d34"\
\
  ],

  "description": "Join us for a lunch and learn session.",

  "where": "Conference Room 1",

  "company": "603dfbc260f4054084125d33",

  "member": "603dfbc260f4054084125d33",

  "limit": 20,

  "links": [\
\
    "https://www.google.com",\
\
    "https://app.officernd.com"\
\
  ],

  "image": "https://www.google.com/image.png"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No