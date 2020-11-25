Design
======
The purpose of this document is to outline the plan for `standards/models.py`
and `urls.py` of the standards server.


Controlled vocabularies
-----------------------
The digital representation of curriculum standards metadata types described below 
is based on terms chosen from controlled vocabularies defined within the context
of a jurisdiction. All examples show in this section assume jutisdicion=Ghana.

When describing the standard statement with name `B4.1.3.1` within the Ghanian
math curriculum standards, we would like to indicate it is part of the "Basic 4"
grade level. Let's look a the some options for representing this information:

1. Add a `grade_level` property (str) whose values are literal values like "Basic 4" or "B4".
2. Make `grade_level` a computed property that parses name `B4.1.3.1` and recognizes
   the presence of the substring `B4` as being a standard within the "Basic 4" level.
3. Add a `grade_level` property (URI) with value `https://qv.link/Ghana/GradeLevels/B4`
   where `https://qv.link` is the server hosting the controlled vocabulary,
   `Ghana` is the jurisdiction name, `GradeLevels` is the name of the controlled vocabulary,
   and `B4` is the term name. Using URIs as property values is a superset of
   literal values that provides some additional affordances for data consumers:
    - Browse `https://qv.link/Ghana/`: all controlled vocabularies define within the Ghana jurisdiction
    - Browse `https://qv.link/Ghana/GradeLevels`: the Ghana grade levels vocabulary, see [POC](https://github.com/GROCCAD/standards-ghana/blob/main/terms/GradeLevels.yml).
    - Browse `https://qv.link/Ghana/GradeLevels/B4`: a webpage with human-readable info about label:"Basic 4" term
    - GET `https://qv.link/Ghana/GradeLevels/B4.json`: all metadata for this term as JSON
    - GET `https://qv.link/Ghana/GradeLevels/B4.{fmt}`: all metadata for this term as `{fmt}`


Terms
-----
The controlled vocabulary term for the Basic 4 level can be referenced in multiple
equivalent ways:

 - canonical representation as a URI `https://qv.link/Ghana/GradeLevels/B4`
 - name:`B4` within the `GradeLevels` Ghana vocabulary (assume names unique within vocabulary)
 - path:`B4` within the `GradeLevels` Ghana vocabulary (for hierarchical vocabularies,
   path is `/`-joined string of the taxon path, e.g. `math/algebra/quadratic_equations`.
 - tags:[`B4` (in Ghana), `Ghana:B4`, `Ghana:GradeLevels/B4`, `qv:Ghana/GradeLevels/B4`].
 - wikidata_id:`Q12929192`


The metadata associated with the term is can be requested in multiple representations:

 - `https://qv.link/Ghana/GradeLevels/B4`: human-readable webpage
 - `https://qv.link/Ghana/GradeLevels/B4.json`: JSON (as used by frontend and apps)
 - `https://qv.link/Ghana/GradeLevels/B4.jsonld`: linked data as JSON-LD
 - `https://qv.link/Ghana/GradeLevels/B4.rdf`: linked data as SKOS in RDF



Jurisdictions
-------------



Standards documents
-------------------



Standards statements
--------------------

 - canonical representation as a URI `https://qdata.link/Ghana/Math/B4.1.3.1`
   which is a browsable webpage
 - `https://qdata.link/Ghana/Math/B4.1.3.1.json`: JSON (as used by frontend and apps)
 - `https://qdata.link/Ghana/Math/B4.1.3.1.csv`: CSV of standard and its components as rows
 - `https://qdata.link/Ghana/Math/B4.1.3.1.case.json`: CASE JSON of CFItem
 - `https://qdata.link/Ghana/Math/B4.1.3.1.jsonld`: linked data as JSON-LD (schema?)
 - `https://qdata.link/Ghana/Math/B4.1.3.1.asn.rdf`: ASN RDF

