Design
======
The purpose of this page is to give a high level overview of the design decisions
that went into the Repository of Organized Curriculums (ROC) data model.



Jurisdictions
-------------
A namespace that corresponds to some-real world region or organization, e.g.,
`Ghana`, `USA`, `KhanAcademy`, `LE`, etc. The `Global` jurisdiction is used as
the namespace for ROC data model constants (e.g. `digitzation_methods`,
`content_kinds`, `publication_statuses`, etc.).


Controlled vocabularies and terms
---------------------------------
The digital representation of curriculum standards metadata types described below 
is based on terms chosen from controlled vocabularies defined within the context
of a jurisdiction. All examples show in this section assume jurisdiction=Ghana.

When describing the standard statement with notation `B4.1.3.1` within the Ghanian
math curriculum standards, we would like to indicate it is part of the "Basic 4"
grade level, but instead of using a string value we will use a URI property.
The Uniform Resource Identifier (URI) value `https://rocdata.global/Ghana/terms/GradeLevels/B4`
is an example of one such identifiers, specifically the identifiers for the "Basic 4"
grade level within the Ghana educational system. In this URI, `https://rocdata.global`
is the server hosting the controlled vocabulary, `Ghana` is the jurisdiction name,
`GradeLevels` is the name of the controlled vocabulary, and `B4` is the term name.
Using URIs as property values provides the following affordances for data consumers:



Standards documents and standard nodes
--------------------------------------


 

Standards crosswalks
--------------------




Content collections and content nodes
-------------------------------------



Content correlations
--------------------
