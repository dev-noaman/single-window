# Post a comment/comments about a specific ticket

Source: https://developer.officernd.com/reference/ticketcommentscontroller_addcomment

ticketId

string

required

ticket id

orgSlug

string

required

organization slug

text

string

required

The text of the comment.

member

string

required

The member that posts the comment.

isPublic

boolean

required

Boolean that shows whether the comment is public.
Comments coming from members can only have public set to "true".

truefalse

# `` 201

object

\_id

string

The \_id of the item.

text

string

The text of the comment.

target

string

The \_id of the target item.

targetType

string

enum

The type of the target item.

`team``member``payment``issue`

member

string

The \_id of the member who posted the comment.

isPublic

boolean

Boolean that shows whether the comment is public.

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

     --url https://app.officernd.com/api/v2/organizations/orgSlug/ticket-comments/ticketId \

     --header 'accept: application/json' \

     --header 'content-type: application/json' \

     --data '{"isPublic":true}'
```

```

xxxxxxxxxx



{

  "_id": "6985f1674cc913fc5ac7bf84",

  "text": "This is the comment text",

  "target": "6985f1674cc913fc5ac7bf85",

  "targetType": "issue",

  "member": "6985f1674cc913fc5ac7bf86",

  "isPublic": true

}
```

Updated 5 months ago

* * *

Did this page help you?

Yes

No