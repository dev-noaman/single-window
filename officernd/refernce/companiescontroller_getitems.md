# Get companies

Source: https://developer.officernd.com/reference/companiescontroller_getitems

orgSlug

string

required

organization slug

\_id

string

The exact id of the company you are looking for.

name

string

The exact name of the company you are looking for.

location

string

Filter by location id.

status

string

enum

Filter by the status of the company. Accepts either a single status value or an array operator filter for multiple values.
Available status values: active, former, pending, inactive, not\_approved, drop-in, lead

status=activeactiveformerpendinginactivenot\_approveddrop-inlead

Allowed:

`active``former``pending``inactive``not_approved``drop-in``lead`

createdAt

string

Support date comparison filters: $gt, $gte, $lt, $lte

modifiedAt

string

Support date comparison filters: $gt, $gte, $lt, $lte

properties

string

Filter by custom properties. Uses deepObject style in query. Only string values are supported.

$select

string

Select fields to return

$cursorNext

string

$cursorPrev

string

$limit

number

$sort

json

Sort by name,email,startDate and direction (asc, desc)

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

properties

object

An object that contains all custom properties that can be applied to the item.

Has additional fields

\_id

string

The id of the company.

startDate

date-time

The start date of the company.

location

string

The location of the company.

name

string

The name of the company.

description

string

The description of the company.

email

string

The email of the company.

image

string

The logo/image URL of the company.

url

string

The website URL of the company.

address

object

The address details of the company.

address object

status

string

enum

The status of the company.

`active``former``pending``inactive``not_approved``drop-in``lead`

billingDetails

object

The billing details of the company.

billingDetails object

portalPrivacy

object

The portal privacy settings of the company.

portalPrivacy object

hasActiveMembersAllowance

boolean

Indicates whether the "Active members allowance" setting is enabled.

activeMembersAllowanceLimit

number

The limit of active member seats that can be added to the company.

tags

array of strings

An array of tags associated with the company.

tags

createdAt

date-time

The date of creation of the company.

createdBy

string

The user that created the company.

modifiedAt

date-time

The date of the last update the company.

modifiedBy

string

The user that last updated the company.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/companies \

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
      "properties": {\
\
        "customProperty1": "value1",\
\
        "customProperty2": "value2"\
\
      },\
\
      "_id": "603dfbc260f4054084125d33",\
\
      "startDate": "2025-02-25T00:00:00.000Z",\
\
      "location": "603dfbc260f4054084125d33",\
\
      "name": "My Company",\
\
      "description": "This is the description of the company.",\
\
      "email": "example@gmail.com",\
\
      "image": "image-url.com",\
\
      "url": "company-url.com",\
\
      "address": {\
\
        "country": "United States",\
\
        "state": "California",\
\
        "city": "San Francisco",\
\
        "street": "123 Main St, San Francisco, CA 94105",\
\
        "zip": "94105"\
\
      },\
\
      "status": "active",\
\
      "billingDetails": {\
\
        "billingName": "Example Billing Name",\
\
        "vatNumber": "123456789",\
\
        "registrationNumber": "987654321",\
\
        "paymentMethod": "Cash",\
\
        "billingAddress": {\
\
          "country": "United States",\
\
          "state": "California",\
\
          "city": "San Francisco",\
\
          "street": "123 Main St, San Francisco, CA 94105",\
\
          "zip": "94105"\
\
        }\
\
      },\
\
      "portalPrivacy": {\
\
        "isVisible": true,\
\
        "showContactDetails": false,\
\
        "showSocialProfiles": true\
\
      },\
\
      "hasActiveMembersAllowance": true,\
\
      "activeMembersAllowanceLimit": 10,\
\
      "tags": [\
\
        "tag1",\
\
        "tag2",\
\
        "tag3"\
\
      ],\
\
      "createdAt": "2025-02-25T00:00:00.000Z",\
\
      "createdBy": "603dfbc260f4054084125d33",\
\
      "modifiedAt": "2025-02-25T00:00:00.000Z",\
\
      "modifiedBy": "603dfbc260f4054084125d33"\
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