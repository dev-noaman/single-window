# Get benefit

Source: https://developer.officernd.com/reference/benefitscontroller_getitem

benefitId

string

required

benefit id

orgSlug

string

required

organization slug

# `` 200

object

\_id

string

The \_id of the benefit.

name

string

The name of the benefit.

description

string

A short description of the benefit.

content

string

A longer description of the benefit.

url

string

An external URL associated with the benefit.

image

string

The image of the benefit.

coverImage

string

The cover image of the benefit.

category

string

The category of the benefit. If you create multiple benefits with matching categories,
they'll be grouped in the members portal under the same category.

locations

array of strings

An array containing the \_ids of locations for which the benefit applies.
If left empty the benefit will apply for all locations.

locations

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/benefits/benefitId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "_id": "603dfbc260f4054084125d31",

  "name": "Benefit Name",

  "description": "Example Description",

  "content": "<p>Example Content</p>",

  "url": "exampleExternalLink.com",

  "image": "exampleImageLink.com",

  "coverImage": "exampleImageLink.com",

  "category": "Example Category",

  "locations": [\
\
    "603dfbc260f4054084125f34"\
\
  ]

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No