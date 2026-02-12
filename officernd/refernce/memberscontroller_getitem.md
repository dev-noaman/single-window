# Get member

Source: https://developer.officernd.com/reference/memberscontroller_getitem

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

country

string

The country of the address.

state

string

The state of the address.

city

string

The city of the address.

street

string

The street of the address.

zip

string

The zip of the address.

billingDetails

object

The billing details of the member.

billingName

string

The billing name of the member that will appear on transactions and invoices.

vatNumber

string

The VAT number of the member.

registrationNumber

string

The registration number of the member.

paymentMethod

string

The payment method of the member.

billingAddress

object

The billing address of the member.

billingAddress object

portalPrivacy

object

The portal privacy settings of the member.

isVisible

boolean

Determines whether the member's profile is visible in the members portal.

showContactDetails

boolean

Determines whether the member's contact details are visible in the members portal.

showSocialProfiles

boolean

Determines whether the member's (Twitter, LinkedIn, Facebook, Instragram) socials are visible in the members portal.

socialProfiles

object

Social media profiles of the member.

linkedin

string

LinkedIn profile URL or handle

twitter

string

Twitter/X profile URL or handle

instagram

string

Instagram profile URL or handle

facebook

string

Facebook profile URL

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/members/memberId \

     --header 'accept: application/json'
```

```

xxxxxxxxxx



{

  "properties": {

    "customProperty1": "value1",

    "customProperty2": "value2"

  },

  "_id": "603dfbc260f4054084125d33",

  "name": "John Doe",

  "email": "john.doe@example.com",

  "phone": "012-345-6789",

  "image": "image-url.com",

  "description": "John Doe is an example member of the organization.",

  "location": "603dfbc260f4054084125d33",

  "company": "603dfbc260f4054084125d33",

  "status": "active",

  "startDate": "2025-01-01T00:00:00.000Z",

  "isBillingPerson": true,

  "isContactPerson": true,

  "address": {

    "country": "United States",

    "state": "California",

    "city": "San Francisco",

    "street": "123 Main St, San Francisco, CA 94105",

    "zip": "94105"

  },

  "billingDetails": {

    "billingName": "Example Billing Name",

    "vatNumber": "123456789",

    "registrationNumber": "987654321",

    "paymentMethod": "Cash",

    "billingAddress": {

      "country": "United States",

      "state": "California",

      "city": "San Francisco",

      "street": "123 Main St, San Francisco, CA 94105",

      "zip": "94105"

    }

  },

  "portalPrivacy": {

    "isVisible": true,

    "showContactDetails": false,

    "showSocialProfiles": true

  },

  "socialProfiles": {

    "linkedin": "https://linkedin.com/in/johndoe",

    "twitter": "https://twitter.com/johndoe",

    "instagram": "https://instagram.com/johndoe",

    "facebook": "https://facebook.com/johndoe"

  },

  "createdAt": "2025-01-01T00:00:00.000Z",

  "modifiedAt": "2025-01-01T00:00:00.000Z",

  "tags": [\
\
    "vip",\
\
    "early-adopter"\
\
  ]

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No