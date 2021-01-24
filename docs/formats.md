Formats
=======

Each "resource" in the ROC server is accessible in several data formats.
Using the example of the Term "Mathematics" within the Ghana:Subjects controlled
vocabulary, https://rocdata.global/Ghana/terms/Subjects/Mathematics 

 - https://rocdata.global/Ghana/terms/Subjects/Mathematics = canonical URI of the
   resource, which returns different formats depending on request headers.
   By default, returns the `.html` format (see next).
 - https://rocdata.global/Ghana/terms/Subjects/Mathematics.html = HTML browsing interface
 - https://rocdata.global/Ghana/terms/Subjects/Mathematics.json = JSON (as used by frontend and apps)
 - https://rocdata.global/Ghana/terms/Subjects/Mathematics.yaml = YAML [TODO]
 - https://rocdata.global/Ghana/terms/Subjects/Mathematics.csv = CSV [TODO]
 
 
 For standards documents and standard nodes, the following formats are can be 
 implemented in the future based on user needs:

 - `https://rocdata.global/Ghana/standardnodes/S12345678.asn.rdf`: ASN RDF graph
 - `https://rocdata.global/Ghana/standardnodes/S12345678.case.json`: CASE JSON (tree of `CFItem`s)


Bulk data exports
-----------------
Other "bulk exports" formats are available for specific use cases like the development
of machine learning algorithms for automated discovery of
[content correlations][./automation/content_correlations_discovery.md]
and [standards crosswalks](./automation/standards_crosswalk_discovery.md).

