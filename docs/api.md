ROC API
=======
The purpose of page is to give a high level overview of the ROC server API.



Jurisdictions
-------------
A namespace that corresponds to some-real world region or organization, e.g.,
`Ghana`, `USA`, `KhanAcademy`, `LE`, etc.

  - Examples https://rocdata.global/Ghana and https://rocdata.global/KA .

The `Global` jurisdiction, https://rocdata.global/Global , is used for ROC data
model constants (e.g. `digitzation_methods`, `content_kinds`, `publication_statuses`).

TODO: figure


Controlled vocabularies and terms
---------------------------------
The digital representation of curriculum standards metadata types described below 
is based on terms chosen from controlled vocabularies defined within the context
of a jurisdiction. All examples show in this section assume jurisdiction=Ghana.

  - Browse https://rocdata.global/Ghana/terms : all controlled vocabularies define within the Ghana jurisdiction
  - Browse https://rocdata.global/Ghana/terms/GradeLevels : the Ghana grade levels vocabulary,
    see also [standards-ghana/terms/GradeLevels](https://github.com/rocdata/standards-ghana/blob/main/terms/GradeLevels.yml).
  - Browse https://rocdata.global/Ghana/terms/GradeLevels/B4 : a webpage with human-readable info about the term "Basic 4"
  - GET https://rocdata.global/Ghana/terms/GradeLevels/B4.json : metadata for term `B4` as JSON


Term relations
--------------

`{juri}/termrels/{jurisdiction}/{termrel.id}`



Standards documents and standard nodes
--------------------------------------

`{juri}/documents/{document.id}`

`{juri}/standardnodes/{snode.id}`

 

Standards crosswalks
--------------------

`{juri}/standardscrosswalks/{sc.id}`

`{juri}/standardnoderels/{stdrel.id}`




Content collections and content nodes
-------------------------------------


`{juri}/contentcollections/{cc.id}`

`{juri}/contentnodes/{contentnode.id}`

`{juri}/contentnoderels/{cnode.id}`





Content correlations
--------------------

`{juri}/contentcorrelations/{cs.id}`

`{juri}/contentstandardrels/{csr.id}`

