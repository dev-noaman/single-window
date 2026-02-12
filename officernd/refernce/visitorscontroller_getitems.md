# Get visitors

Source: https://developer.officernd.com/reference/visitorscontroller_getitems

orgSlug

string

required

organization slug

\_id

string

Filter by visitor id. Supports both single id values (e.g., \_id=66623dc53090242657393910) and array operations (e.g., \_id\[$in\]=66623dc53090242657393910,66623dbf309024265739390a).
Note: Multiple values in simple string format (e.g., \_id=66623dc53090242657393910,66623dbf309024265739390a) are not allowed - use \_id\[$in\] format instead.

name

string

Filter by exact visitor name.

email

string

Filter by exact visitor email.

type

string

enum

Filter by the type of the visitor.

receptionpreregistrationreception

Allowed:

`preregistration``reception`

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

The \_id of the visitor.

name

string

The full name of the visitor.

email

string

The email address of the visitor.

phone

string

The phone number of the visitor.

description

string

Description of the visitor.

member

string

Reference to the member that the visitor is visiting.

company

string

Reference to the company that the visitor is visiting.

type

string

enum

The type of the visitor. Can be one of the following - reception, preregistration.

`preregistration``reception`

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/visitors \

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
      "_id": "603dfbc260f4054084125d39",\
\
      "name": "John Doe",\
\
      "email": "johnDoe@email.com",\
\
      "phone": "1234567890",\
\
      "description": "John Doe is visiting the office for a meeting.",\
\
      "member": "603dfbc260f4054084125d38",\
\
      "company": "603dfbc260f4054084125d34",\
\
      "type": "reception"\
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