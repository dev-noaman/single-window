# Check Out a Member

Source: https://developer.officernd.com/reference/checkinscontroller_checkout

memberId

string

required

member id

orgSlug

string

required

organization slug

# `` 200

object

\_id

string

The \_id of the check-in.

start

date-time

Contains the start date of the check-in.

end

date-time

Contains the end date of the check-in.

location

string

The \_id of the location associated with the check-in.

company

string

The \_id of the company associated with the check-in.

member

string

The \_id of the member associated with the check-in.

booking

string

The \_id of the booking associated with the check-in.

pass

string

The \_id of the pass associated with the check-in.

resourceType

string

The resourceType of the booking associated with the check-in.

source

string

The source associated with the check-in.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/checkins/checkout/memberId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "_id": "6080186f490fcf6e0547ec57",

  "start": "2024-10-31T13:15:00.000Z",

  "end": "2024-10-31T15:30:00.000Z",

  "location": "6080186f490fcf6e0547ec57",

  "company": "6080186f490fcf6e0547ec57",

  "member": "6080186f490fcf6e0547ec57",

  "booking": "6080186f490fcf6e0547ec57",

  "pass": "6080186f490fcf6e0547ec57",

  "resourceType": "hotdesk",

  "source": "admin"

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No