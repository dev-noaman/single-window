# Retrieve all posts

Source: https://developer.officernd.com/reference/postscontroller_getitems

orgSlug

string

required

organization slug

\_id

array of strings

Filter by post id.

\_id
ADD string

locations

array of strings

Filter by location id.

locations
ADD string

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

The \_id of the post.

title

string

The title of the post.

description

string

The content the post.

locations

array of strings

An array with the ids of all locations in which the post is visible.

locations

isPinned

boolean

Shows if the post is pinned to the top.

type

string

enum

The type of the post.

`info``important``event`

url

string

An additional url that is shown in the post.

image

string

The url of the image of the post.

member

string

The \_id of the member that created the post.

company

string

The \_id of the company that created the post.

createdBy

string

The user that created the post.

createdAt

string

The time when the post was created.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/posts \

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
      "_id": "",\
\
      "title": "",\
\
      "description": "",\
\
      "locations": "",\
\
      "isPinned": "",\
\
      "type": "",\
\
      "url": "",\
\
      "image": "",\
\
      "member": "",\
\
      "company": "",\
\
      "createdBy": "",\
\
      "createdAt": ""\
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