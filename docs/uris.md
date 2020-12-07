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
resources' `get_absolute_url()` methods in order to allow local browsing.



Publishing context
------------------
When exporting data, external resources are identified by their `canonical_uri`.

The `canonical_uri` for internal URIs is computed depending on the "publishing context"
for the jurisdiction, which determines the appropriate hostname for the URIs as
described below.

## Standards server
The publishing context `standardsserver` corresponds to the hostname: ...

### Github pages
The publishing context `githubpages` with can be used when the official data
source for a given jurisdiction is published to a github pages website.

### w3id.org  
The publishing context `w3id.org` is used to assign URIs that start with hostname
`https://w3id.org` which in turn redirect to another server or github page.
For maximum flexibility, `https://w3id.org` URIs will be used as canonical URIs.
See https://github.com/perma-id/w3id.org for more info about the redirect service.



When creating the export (static site generator mode), the hostname for URIs is
determined by [HOST headers](https://github.com/django/django/blob/master/django/http/request.py#L109-L126)
by the HTTP client and may need to be manually modified.



Resolving URIs
--------------
When encountering a URI reference to a resource, we follow the same process as
during publishing in order to find the referenced object, including internal URIs,
mirrored external URIs, and external URIs.
