Domain Requirements Specification
=================================
The purpose of this document is to describe the needs and intended use cases for
the Repository of Organized Curriculums (ROC) data model and the its reference
implementation as the `rocserver` project.


Domain overview
---------------
For a detailed introduction to the domain of digital curriculum standards documents
and their use in education, see the report
"Digitizing Curriculum Standards to Unlock the Potential of Open Educational Resources in a Global Context".




Domain problems
---------------
The problems can be summarized as (1) lack of access to curriculum standards data
in machine-readable formats, and (2) lack of tools for creating, storing, and 
exchanging curriculum alignment information.


### Curriculum standards data problems

 - Curriculum standards for most countries is only available in "analog formats"
   like print documents and PDFs.
 - The lack of awareness by ministries of education and curriculum bodies about
   the benefits and use cases of digital curriculum standards.
 - The lack of resources and expertise in MoEs and curriculum bodies to undertake
   new digital projects.

School administrators and teachers wishing to create standards-aligned learning
experiences often have to transcribe curriculum standards documents into Excel
sheets in order to use them as part of course preparation and lesson planning.
Similarly, content creators and content repository administrators must undertake
standards digitization process in order to extract the curriculum standards data
from unstructured documents (print and PDF) and import it into their platforms.

The lack of curriculum standards information available in machine-readable form
also poses a significant obstacle for the process of curriculum alignment
(the cataloging of learning experiences according based on their relevance for
the specific learning objectives specified in curriculum standards), which we
will discuss next.

### Curriculum alignment problems

 - The utility of Open Educational Resources (OERs) is without if the cataloging
   work needed to organize them according to needs of the local educational system
   (subjects, grade level, topics, and individual learning objectives).
   The lack of catalog (curriculum alignment data) makes is difficult for librarians,
   teacher trainers, teachers, and students to find relevant resources.  
 - The task of curriculum alignment (cataloging of learning resources c1 c2 .. cN 
   according to relevant curriculum standards sX1 sX2 .. sXn of country X) is
   requires curriculum expertise, context awareness and is very time consuming
   to carry out for large content collections.
 - The task of curriculum alignment for ALL countries in the world is huge:
   consider large content collections can have N=10000 learning resources,
   and each the curriculum standards of each country can have n=1000 standards.
 - Every learning platforms provides a different mechanism for representing
   content correlations (e.g. by assigning standards-alignment tags), and the
   process of curriculum alignment is often done manually (e.g. browse+search+add tags)
   through time consuming and error-prone workflows.
 - There are no methods for exchange content correlations data between platforms.



Domain opportunities
--------------------

### Spreadsheets
 - Government bodies can easily publish curriculum standards data as spreadsheets.
   Instead of publishing the curriculum standards spreadsheet as a excel table
   embedded in a Word document, converted to a PDF, just publish standards spreadsheet.
 - Access to spreadsheets of curriculum standards information will be immediately
   useful for teachers (these are the tools of the trade they are most familiar with)
 - Spreadsheets data in any format can be easily converted to ROC data format and
   imported into the `rocserver` by writing an "importer integration script" or
   by simply re-organizing the spreadsheet data to fit a provided ROC data template).
 - The `rocserver` application allows all (1) curriculum standards, (2) content
   correlations, and (3) standards crosswalks data to be exported as various
   spreadsheet formats (CSV, .ods, .xlsx, .xls, gsheets, etc.)


### Digital-first curriculum data

 - Apps for teachers (browse local standard for country X and find relevant learning resources)
 - Facilitate the adoption of new standards (e.g. new KICD CBC and Ghana 2019 standards)
   by making the information widely available coming from the authoritative source.

### Easy data publishing in GitHub repositories
 - Jurisdiction = GitHub repo
 - Website as GitHub pages

### Machine learning
 - Recent advances in language models offer an opportunity to learn "deep" structure
   and the nuances of curriculum alignment task (semantic matching = the real goal),
   and baseline categorization methods based on keywords and old-school similarity metrics.




Publishing
----------

### Jurisdictions 

A namespace that corresponds to some-real world region or organization, e.g.,
`Ghana`, `USA`, `KhanAcademy`, `LE`, etc. The `Global` jurisdiction is used as
the namespace for ROC data model constants (e.g. `digitzation_methods`,
`content_kinds`, `publication_statuses`, etc.). 


### Controlled vocabularies and terms 

The digital representation of curriculum standards metadata types described
below is based on terms chosen from controlled vocabularies defined within the
context of a jurisdiction. All examples show in this section assume jurisdiction=Ghana. 

When describing the standard statement with notation `B4.1.3.1` within the
Ghanian math curriculum standards, we would like to indicate it is part of the
"Basic 4" grade level, but instead of using a string value we will use a URI property.
The Uniform Resource Identifier (URI) value `https://rocdata.global/Ghana/terms/GradeLevels/B4`
is an example of one such identifiers, specifically the identifiers for the
"Basic 4" grade level within the Ghana educational system. In this URI,
`https://rocdata.global` is the server hosting the controlled vocabulary,
`Ghana` is the jurisdiction name, `GradeLevels` is the name of the controlled
vocabulary, and `B4` is the term name. Using URIs as property values provides
the following affordances for data consumers:


### Standards

Curriculum standards documents and the individual standards nodes they consist of.



### Content

Content collections and content nodes they consist of. We need to have a way to
refer to individual resources, so the data model assumes `source_url` present at
the minimum, with preference for additional metadata like `source_domain` and `source_id`.



### Content correlations

Sets of content-standard associations that indicate a content resource is useful,
relevant, or related to a specific educational standard node (an element of a
standards document).

