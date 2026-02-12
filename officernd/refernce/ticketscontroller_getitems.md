# Get tickets

Source: https://developer.officernd.com/reference/ticketscontroller_getitems

orgSlug

string

required

organization slug

$select

string

Select fields to return

$cursorNext

string

$cursorPrev

string

$limit

number

# `` 200

object

rangeStart

number

rangeEnd

number

cursorNext

string

cursorPrev

string

results

array of objects

results

object

\_id

string

The \_id of the item.

type

string

The \_id of the ticket options.

severity

string

The \_id of the ticket severity.

priority

string

The \_id of the ticket priority

company

string

The \_id of the company with which the ticket will be associated.

member

string

The \_id of the member who has created the ticket.

location

string

The \_id of the location with which the ticket is associated.

status

string

enum

The status of the ticket.

`open``new``pending``resolved`

assignedTo

string

The \_id of the location to whom the ticket is assigned.

resolvedDate

string

The date of the resolution date of the ticket.

attachments

array of strings

An array of strings containing the URLs of all images attachments

attachments

subject

string

The ticket description.

message

string

The ticket message.

Updated 5 months ago

* * *

Did this page help you?

Yes

No

ShellNodeRubyPHPPython

Bearer

```

xxxxxxxxxx

curl --request GET \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/tickets \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "rangeStart": 0,

  "rangeEnd": 0,

  "cursorNext": "string",

  "cursorPrev": "string",

  "results": [\
\
    {\
\
      "_id": "6985f1644cc913fc5ac7bf7b",\
\
      "type": "6985f1644cc913fc5ac7bf7c",\
\
      "severity": "6985f1644cc913fc5ac7bf7d",\
\
      "priority": "6985f1644cc913fc5ac7bf7e",\
\
      "company": "6985f1644cc913fc5ac7bf7f",\
\
      "member": "6985f1644cc913fc5ac7bf80",\
\
      "location": "6985f1644cc913fc5ac7bf81",\
\
      "status": "open",\
\
      "assignedTo": "6985f1644cc913fc5ac7bf82",\
\
      "resolvedDate": "2025-03-01T00:00:00.000Z",\
\
      "attachments": [\
\
        "https://example.com/image.jpg",\
\
        "https://example.com/image2.jpg"\
\
      ],\
\
      "subject": "Support query",\
\
      "message": "This is the message of the ticket"\
\
    }\
\
  ]

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No