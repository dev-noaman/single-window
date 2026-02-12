# Get members

Source: https://developer.officernd.com/reference/memberscontroller_getitems

orgSlug

string

required

organization slug

\_id

string

Filter by the member id.

name

string

Filter by the name of the member. This returns a result only if the name is an exact match.

email

string

Filter by the email of the member. This returns a result only if the email is an exact match.

location

string

Filter by the location id of the member.

company

string

Filter by the company id of the member.

status

string

enum

Filter by the status of the member.
Accepts either a single status value or an array operator filter for multiple values.

```undefined
        Single value: status=active
        Multiple values: status[$in]=active,pending

        Available status values: active, former, pending, contact, not_approved, drop-in, lead
```

status=activeactiveformerpendingcontactnot\_approveddrop-inlead

Allowed:

`active``former``pending``contact``not_approved``drop-in``lead`

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

Sort by name,email,location,company,status,modifiedAt and direction (asc, desc)

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

The unique identifier of the member.

name

string

The exact name of the item you are looking for. Also, you can use this property to perform a wildcard match.

email

string

The email of the member.

phone

string

The primary phone number of the member.

image

string

The logo/image URL of the member.

description

string

The description/bio of the member.

location

string

Reference to the location of the member.

company

string

Reference to the company the member belongs to.

status

string

enum

The status of the member.

`active``former``pending``contact``not_approved``drop-in``lead`

startDate

date-time

The starting date of the member.

isBillingPerson

boolean

True if the member is the billing person of his company and receives all the invoices.

isContactPerson

boolean

True if the member is a contact person in his company.

address

object

The address details of the member.

address object

billingDetails

object

The billing details of the member.

billingDetails object

portalPrivacy

object

The portal privacy settings of the member.

portalPrivacy object

socialProfiles

object

Social media profiles of the member.

socialProfiles object

createdAt

date-time

The date of creation of the member. It may be different from the start date.

modifiedAt

date-time

The date of the last update of the member.

tags

array of strings

An array of tags associated with the member.

tags

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/members \

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
      "name": "John Doe",\
\
      "email": "john.doe@example.com",\
\
      "phone": "012-345-6789",\
\
      "image": "image-url.com",\
\
      "description": "John Doe is an example member of the organization.",\
\
      "location": "603dfbc260f4054084125d33",\
\
      "company": "603dfbc260f4054084125d33",\
\
      "status": "active",\
\
      "startDate": "2025-01-01T00:00:00.000Z",\
\
      "isBillingPerson": true,\
\
      "isContactPerson": true,\
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
      "socialProfiles": {\
\
        "linkedin": "https://linkedin.com/in/johndoe",\
\
        "twitter": "https://twitter.com/johndoe",\
\
        "instagram": "https://instagram.com/johndoe",\
\
        "facebook": "https://facebook.com/johndoe"\
\
      },\
\
      "createdAt": "2025-01-01T00:00:00.000Z",\
\
      "modifiedAt": "2025-01-01T00:00:00.000Z",\
\
      "tags": [\
\
        "vip",\
\
        "early-adopter"\
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