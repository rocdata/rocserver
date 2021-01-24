Kolibri channel content collections
===================================

A Kolibri channel consists of two parts:
 - Metadata stored in sqlite3 DB file. The channel DB file can downloaded from
   URL like `/content/databases/{{channel_id}}.sqlite3` from any instance of the Kolibri application,
   Kolibri Studio, or obtained through direct file transfer.
 - A collection of files stored in `/content/storage/{x}/{y}/{xyz.......}.ext`

For the purpose of importing Kolibri channels as content collections, we need to
import only the content metadata from the Kolibri database file.

Usage
-----

1. Obtain the `channel_id` of the channel you want to import. You can find the
   a channel's ID from the URL when viewing the channel in Kolirbi or Kolibri Studio.
2. Run the script in the [rocdata/contentcollections-kolibri](https://github.com/rocdata/contentcollections-kolibri)
   repository to obtain the kolibritrees JSON dump of the channel database:  
   `./kolibri_db/reader.py --channel_id=<channel_id>`
3. Import the channel as a content collection using the rocserver management command:  
   ```
   ./manage.py ccimport_kolibri  \
      --jurisdiction LE \
      --country US \
      --name <shortname> \
      --source_domain <sourcewebsiteurl> \
      --source_url <weburlofcollection> \
      --kolibritree_url=<urlwherejsoncanbedownloadedfrom>
    ```
    where `<shortname>` must be a unique, short identifier for the collection,
    e.g. `KA-en`.

The following properties of the content collection will be set by default:
 - `collection_id`: set to `channel_id`
 - `version`: taken from imported JSON [TODO]
 - `publication_status="publicdraft"`. This can be chanced to "public" through admin.
 - `subjects=[]`: can add subject references (ManyToManyField relations to terms in vocabularies of kind `subjects`.
 - `education_levels=[]`: can add grade levels references (relations to terms in vocabularies of kind `education_levels`.
