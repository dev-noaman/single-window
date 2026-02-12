# Retrieve all custom properties

Source: https://developer.officernd.com/reference/custompropertiescontroller_getitems

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

The \_id of the custom property.

key

string

The name of the custom property. This is the unique identifier which you use when applying the property.

title

string

The title of the custom property.

placeholder

string

The placeholder of the custom property.

type

string

The type of the custom property.

privacy

string

The privacy setting of the custom property.

targets

array of strings

The system entities for which the custom property can be applied.

targets

values

array of strings

An array containg the possible values for custom properties of type "Select" and "Multi-Select".

values

rates

array of strings

An array containg the rates for which the property applies. This relates only to custom properties that apply for bookings.

rates

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/custom-properties \

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
      "_id": "6985f1684cc913fc5ac7bf88",\
\
      "key": "CProp",\
\
      "title": "My Custom Property",\
\
      "placeholder": "Placeholder Value",\
\
      "type": "String",\
\
      "privacy": "admin",\
\
      "targets": [\
\
        "member",\
\
        "contract",\
\
        "plan-fee"\
\
      ],\
\
      "values": [\
\
        "Value1",\
\
        "Value2"\
\
      ],\
\
      "rates": [\
\
        "6985f1684cc913fc5ac7bf89",\
\
        "6985f1684cc913fc5ac7bf8a"\
\
      ]\
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