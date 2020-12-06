Short codes
===========
This page contains info about the short codes used as primary key identifiers
for standards and controlled vocabularies.


Short UUIDs
-----------
Data objects in the standards database have Universally Unique Identifiers (UUIDs),
which are consist of long strings like: `afc7df60-c325-4296-bff4-ea2d73e165c3`.

In order to make these identifiers more user friendly when they appear in URIs,
data exports, and other user-facing aspects we encode these identifiers as "short codes"
generated using the Python library [`shortuuid`](https://github.com/skorokithakis/shortuuid).

Example:
```python
from standards.utils import uuid_to_short_code, short_code_to_uuid

>>> uuid_to_short_code(uuid.UUID('afc7df60-c325-4296-bff4-ea2d73e165c3'))
'ZHgqEmn6BkpKvh6Yt9W82Z'

>>> short_code_to_uuid('ZHgqEmn6BkpKvh6Yt9W82Z')
UUID('afc7df60-c325-4296-bff4-ea2d73e165c3')
```




Short codes
-----------
UUIDs that contain lots of zeros correspond to short codes with very few characters:

```python
>>> uuid_to_short_code(uuid.UUID('00000000-0000-0000-0000-004eeadcba07'))
'BtLVoDR'

>>> short_code_to_uuid('BtLVoDR')
UUID('00000000-0000-0000-0000-004eeadcba07')
```

Using short codes of length 7 taken from an alphabet of 57 characters allows us
to represent approximately 2 Trillion unique IDs:
`57**7` = `1.95 × 10**12` ~= 1.95 TRILLION,
which is an ID space sufficient for encoding standards of many countries with
very small chance of ID collision.



Shorter codes with prefix
-------------------------
The short codes of certain objects include a prefix that gives a hint about the
type of data object it refers to, e.g., the  `R` prefix in the ID `RBtLVoDR`
indicates this is the ID of a relation.
