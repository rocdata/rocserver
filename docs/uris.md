URIs
====

There are several different types of URIs that exist in the system:
 - Internal URIs: for objects that were created on the standards server and thus
   have `self.canonical_uri` == `self.get_absolute_url()`.
 - Mirrored external URIs: vocabulary terms or standards whose official "home"
   is located on an external server, but which have been imported to local server.
   For these `self.canonical_uri == self.source_uri`. Since these resources are
   also "mirrored" locally, they can be browsed at `self.get_absolute_url()`.
 - External URIs: these are references to external resources that cannot be 
   browsed locally, e.g., `target_uri` as part of a relation when `target=None`.


Browsing context
----------------
When accessing a live server instance, navigation links are computed using the
resources' `get_absolute_url()` methods and not using `canonical_uri`s.


Publishing context
------------------
See page on [publishing](./publishing.md) for details about publishing contexts.


Resolving URIs
--------------
When encountering a URI reference to a resource, we follow the same process as
during publishing in order to find the referenced object, including internal URIs,
mirrored external URIs, and external URIs.






Content URLs
------------
Content collections and content nodes are identified by a `source_url`, which is
usually represents a an online location where the resource can be accessed and
downloaded from.


Content IDs
-----------
Content collections and content nodes are identified by a `source_domain` which
represents the hostname where one or more content collections are hosted.
Furthermore, `colletion_id`, `source_id`, `node_id` are also used to identify
content nodes.

