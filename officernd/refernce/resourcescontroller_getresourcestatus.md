# Get resource status

Source: https://developer.officernd.com/reference/resourcescontroller_getresourcestatus

resourceId

string

required

resource id

orgSlug

string

required

organization slug

# `` 200

object

\_id

string

The unique identifier of the resource.

status

string

The current status of the resource (e.g., "available", "occupied", "partially\_occupied", "unavailable"). For parent resources with children, this reflects the overall status including children.

ownStatus

string

The status of the parent resource itself, excluding its children. Only present for parent resources with children (e.g., private offices with office desks). This allows distinguishing between the parent resource's own availability and the overall status that includes children. Example: A private office (team\_room) with two office desks (desk\_tr) where one desk is occupied would have ownStatus="available" (the office itself is not directly occupied) and status="partially\_occupied" (accounting for the occupied child desk). For office desks (desk\_tr), this represents their own status when the parent office affects their availability.

Updated 4 months ago

* * *

Did this page help you?

Yes

No

ShellNodeRubyPHPPython

Bearer

```

xxxxxxxxxx

curl --request GET \

     --url https://app.officernd.com/api/v2/organizations/orgSlug/resources/resourceId/status \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "_id": "603dfbc260f4054084125d39",

  "status": "available",

  "ownStatus": "available"

}
```

Updated 4 months ago

* * *

Did this page help you?

Yes

No