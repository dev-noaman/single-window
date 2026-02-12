# Get the current organization information

Source: https://developer.officernd.com/reference/organizationscontroller_getitem

orgSlug

string

required

organization slug

# `` 200

object

\_id

string

The \_id of the organization.

name

string

The name of the organization.

slug

string

The slug of the organization.

imageUrl

string

The image URL of the organization.

description

string

The description of the organization.

Updated 2 months ago

* * *

Did this page help you?

Yes

No

ShellNodeRubyPHPPython

Bearer

```

xxxxxxxxxx

curl --request GET \

     --url https://app.officernd.com/api/v2/organizations/orgSlug \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "_id": "6080186f490fcf6e0547ec50",

  "name": "Organization Name",

  "slug": "organization-slug",

  "imageUrl": "/image-url.com",

  "description": "Organization Description"

}
```

Updated 2 months ago

* * *

Did this page help you?

Yes

No