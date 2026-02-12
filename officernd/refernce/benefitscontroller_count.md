# Get benefits count by filter

Source: https://developer.officernd.com/reference/benefitscontroller_count

orgSlug

string

required

organization slug

# `` 200

object

total

number

required

groups

array of objects

groups

object

key

string

required

count

number

required

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/benefits/count \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "total": 0,

  "groups": [\
\
    {\
\
      "key": "string",\
\
      "count": 0\
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