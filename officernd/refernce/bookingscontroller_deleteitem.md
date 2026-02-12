# Delete booking

Source: https://developer.officernd.com/reference/bookingscontroller_deleteitem

bookingId

string

required

booking id

orgSlug

string

required

organization slug

isSilent

boolean

Whether to send notifications to the member. If true, a notification will not be sent. If false or not passed at all, the notification will be sent as normal.

truetruefalse

# `` 200

object

properties

object

An object that contains all custom properties that can be applied to the item.

Has additional fields

\_id

string

The \_id of the booking.

timezone

string

The timezone of the booking.

start

string

The start date of the booking.

end

string

The end date of the booking.

recurrence

object

Determines the recurrence rules for the booking.

rrule

string

The recurrence rule for the booking.

exdates

array of date-times

The dates that are marked as an exception from the recurrence.

exdates

seriesStart

string

The start date of the series or standalone booking. For recurring bookings, this refers to the start of the entire series

seriesEnd

string

The end date of the series or standalone booking. For recurring bookings, this refers to the end of the last occurrence.

location

string

The \_id of the location of booking.

company

string

Reference to the company.

member

string

Reference to the member.

resource

string

Reference to the booked resource.

fees

array of objects

Array of items describing how the booking will be charged for.

fees

object

date

date-time

The date of the occurrence the fee has been generated for.

fee

string

The actual charge generated for this occurrence.

extraFees

array of strings

Array of fees generated for the extras.

extraFees

passes

array of strings

Array of passes used for this occurrence.

passes

credits

array of objects

The credits used for the booking.

credits

object

count

number

The number of credits used for the booking.

credit

string

The \_id of the set of credits used for the booking.

coins

array of objects

The coins used for the booking.

coins

object

\_id

string

The \_id of the coin used for the fee.

count

number

The count of the coins used for the fee.

customPrice

number

Used if you want to set a custom price for the booking and ignore the standard rate. Can also be used a in PUT request to update an existing booking.

reference

string

The reference id of the booking.

isCancelled

boolean

Whether the booking got canceled or not.

title

string

Booking title/summary.

rate

string

Reference to the resource rate used for the booking.

description

string

Long description of the booking.

isTentative

boolean

True if the booking is not confirmed. Tentative bookings are not charged.

isFree

boolean

True if the booking is marked as free. If create a booking marked as free, no fees will be added for it.

isAccounted

boolean

True if the booking is marked as accounted.

extras

array of objects

Extras that are added to the booking.

extras

object

View Additional Properties

visitors

array of strings

An array containg a list of all the ids of external visitors associated with the booking.

visitors

members

array of strings

An array containing a list of all the \_ids of teammates associated with the booking. This is possible if the member associated with the booking is part of a company - these company members can be added here.

members

serviceSlots

object

Determines whether the booking has buffer slots before and after.

before

number

The amount of buffer time before the booking in minutes.

after

number

The amount of buffer time after the booking in minutes.

source

string

Shows where the booking was created

createdAt

string

The date when the booking has been created.

createdBy

string

The user that created the booking.

modifiedAt

string

The date of the last update of the booking.

modifiedBy

string

The user that did the last modification to the booking. If no update is made this field will match the createdBy field.

Updated 5 months ago

* * *

Did this page help you?

Yes

No

ShellNodeRubyPHPPython

Bearer

```

xxxxxxxxxx

curl --request DELETE \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/bookings/bookingId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "properties": {

    "customProperty1": "value1",

    "customProperty2": "value2"

  },

  "_id": "603dfbc260f4054084125d39",

  "timezone": "Europe/London",

  "start": "2024-10-31T13:00:00.000Z",

  "end": "2024-10-31T13:30:00.000Z",

  "recurrence": {

    "rrule": "FREQ=WEEKLY;BYDAY=MO,WE,FR;COUNT=10",

    "exdates": [\
\
      "2024-10-31T13:00:00.000Z"\
\
    ]

  },

  "seriesStart": "2024-10-31T13:00:00.000Z",

  "seriesEnd": "2024-10-31T13:30:00.000Z",

  "location": "603dfbc260f4054084125d39",

  "company": "603dfbc260f4054084125d39",

  "member": "603dfbc260f4054084125d39",

  "resource": "603dfbc260f4054084125d39",

  "fees": [\
\
    {\
\
      "date": "2017-10-31T00:00:00.000Z",\
\
      "extraFees": [],\
\
      "credits": [\
\
        {\
\
          "count": 2,\
\
          "credit": "594932ea518f3f150d306c89"\
\
        }\
\
      ],\
\
      "customPrice": 100\
\
    }\
\
  ],

  "reference": "81LCV6S",

  "isCancelled": false,

  "title": "Meeting with John",

  "rate": "603dfbc260f4054084125d39",

  "description": "Meeting with John at the office.",

  "isTentative": true,

  "isFree": false,

  "isAccounted": false,

  "extras": [\
\
    {\
\
      "_id": "603dfbc260f4054084125d39",\
\
      "count": 2\
\
    }\
\
  ],

  "visitors": [\
\
    "603dfbc260f4054084125d36",\
\
    "603dfbc260f4054084125d37"\
\
  ],

  "members": [\
\
    "603dfbc260f4054084125d36",\
\
    "603dfbc260f4054084125d37"\
\
  ],

  "serviceSlots": {

    "before": 10,

    "after": 10

  },

  "source": "admin",

  "createdAt": "2022-02-07T10:03:33.169Z",

  "createdBy": "5bbb155174321f100085eac1",

  "modifiedAt": "2022-02-08T10:03:33.169Z",

  "modifiedBy": "5bbb155174321f100085eac1"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No