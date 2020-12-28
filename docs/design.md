Design
======
The purpose of this design document is to give a high level overview of the
ROCSERVER data model and API.


Jurisdictions
-------------
A namespace that corresponds to some-real world region or organization, e.g.,
Ghana, USA, CCSS, KhanAcademy, LE, etc. The "Global" jurisdiction is used to for
ROCdata constants.


Controlled vocabularies
-----------------------
The digital representation of curriculum standards metadata types described below 
is based on terms chosen from controlled vocabularies defined within the context
of a jurisdiction. All examples show in this section assume jurisdiction=Ghana.

When describing the standard statement with notation `B4.1.3.1` within the Ghanian
math curriculum standards, we would like to indicate it is part of the "Basic 4"
grade level, but instead of using a string value we will use a URI property.
The Uniform Resource Identifiers (URI) value `https://rocdata.global/terms/Ghana/GradeLevels/B4`
where `https://rocdata.global` is the server hosting the controlled vocabulary,
`Ghana` is the jurisdiction name, `GradeLevels` is the name of the controlled vocabulary,
and `B4` is the term name. Using URIs as property values is a superset of
literal values that provides some additional affordances for data consumers:

  - Browse `https://rocdata.global/terms/Ghana/`: all controlled vocabularies define within the Ghana jurisdiction
  - Browse `https://rocdata.global/terms/Ghana/GradeLevels`: the Ghana grade levels vocabulary, see [standards-ghana/terms/GradeLevels](https://github.com/rocdata/standards-ghana/blob/main/terms/GradeLevels.yml).
  - Browse `https://rocdata.global/terms/Ghana/GradeLevels/B4`: a webpage with human-readable info about label:"Basic 4" term
  - GET `https://rocdata.global/terms/Ghana/GradeLevels/B4.json`: all metadata for this term as JSON
  - GET `https://rocdata.global/terms/Ghana/GradeLevels/B4.{fmt}`: all metadata for this term as `{fmt}`



Terms
-----
The controlled vocabulary term for the Basic 4 level can be referenced in multiple
equivalent ways:

 - canonical representation as a URI `https://rocdata.global/terms/Ghana/GradeLevels/B4`)
 - path:`B4` within the `GradeLevels` Ghana vocabulary (for hierarchical vocabularies,
   path can be `/`-joined string of the taxon path, e.g. `math/algebra/quadratic_equations`
   (we assumes path is unique within a vocabulary).
 - tags:[`B4` (in Ghana), `Ghana:B4`, `Ghana:GradeLevels/B4`, `qv:Ghana/GradeLevels/B4`]. (not implemented yet)
 - wikidata_id:`Q12929192` (not implemented yet)


The metadata associated with the term is can be requested in multiple representations:

 - `https://rocdata.global/terms/Ghana/GradeLevels/B4`: human-readable webpage
 - `https://rocdata.global/terms/Ghana/GradeLevels/B4.json`: JSON (as used by frontend and apps)
 - `https://rocdata.global/terms/Ghana/GradeLevels/B4.jsonld`: linked data as JSON-LD (not implemented yet)
 - `https://rocdata.global/terms/Ghana/GradeLevels/B4.rdf`: linked data as SKOS in RDF


Term relations
--------------

`/termrels/{jurisdiction}/{termrel.id}`



Standards documents and nodes
-----------------------------

`/documents/{document.id}`

`/standardnodes/{snode.id}`

 

Standards crosswalks
--------------------

`/standardscrosswalks/{sc.id}`

`/standardnoderels/{stdrel.id}`




Content nodes
-------------

`/contentcollections/{cc.id}`

`/contentnodes/{contentnode.id}`

`/contentnoderels/{cnode.id}`





Content correlations
--------------------

`/contentcorrelations/{cs.id}`

`/contentstandardrels/{csr.id}`

