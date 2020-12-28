Publishing
==========



Publishing context
------------------
When exporting data, external resources are identified by their `canonical_uri`.

The `uri` and `canonical_uri` for internal URIs is computed depending on the 
"publishing context" for the jurisdiction, which determines the appropriate
hostname for URIs. The different publishing contexts are described below.

### Default publishing context
The publishing context `default` corresponds to current hostname, which is determined
dynamically at request time. Usually `http://localhost:8000` or `http://127.0.0.1:8000`.

### Standards server
The publishing context `rocserver` corresponds to the hostname: `https://rocdata.global`.

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




Publishing settings
-------------------
The publishing context name is controlled by the `settings.ROCDATA_PUBLISHING_CONTEXT`,
which in turn is set from the ENV variable `ROCDATA_PUBLISHING_CONTEXT`, or set
to the default value `default`.

The dictionary `settings.ROCDATA_PUBLISHING_CONTEXTS` provides data for all each
publishing context.



Publishing context API
----------------------
The helper method `standards.publishing.get_publshing_context` returns the dictionary
containing the info like this:

```python
    {
        "scheme": "https",
        "netloc": "https://w3id.org",
        "path_prefix": "/rocdata",
    }
```

The helper function `standards.publishing.build_absolute_uri(path, publishing_context=None, request=None)`
can be used to obtain the absolute URI of for any path `path`, in the publishing
context `publishing_context` (if not provided, the default publishing context is used).
The keyword argument `request` is required for the default context.




