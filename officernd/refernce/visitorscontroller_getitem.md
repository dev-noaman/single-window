# Get visitor

Source: https://developer.officernd.com/reference/visitorscontroller_getitem

visitorId

string

required

visitor id

orgSlug

string

required

organization slug

# `` 200

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/visitors/visitorId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "_id": "603dfbc260f4054084125d39",

  "name": "John Doe",

  "email": "johnDoe@email.com",

  "phone": "1234567890",

  "description": "John Doe is visiting the office for a meeting.",

  "member": "603dfbc260f4054084125d38",

  "company": "603dfbc260f4054084125d34",

  "type": "reception"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No