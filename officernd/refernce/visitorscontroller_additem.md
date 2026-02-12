# Add new visitor

Source: https://developer.officernd.com/reference/visitorscontroller_additem

orgSlug

string

required

organization slug

name

string

required

The full name of the visitor.

type

string

enum

required

The type of the visitor. Can be one of the following - reception, preregistration.

preregistrationreception

Allowed:

`preregistration``reception`

email

string

The email address of the visitor.

member

string

Reference to the member that the visitor is visiting.

phone

string

The phone number of the visitor.

company

string

The company of the visitor.

# `` 201

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

curl --request POST \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/visitors \

     --header 'accept: application/json' \

     --header 'content-type: application/json' \

     --data '

{

  "type": "preregistration"

}

'
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