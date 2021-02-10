Standards crosswalk discovery
=============================
Knowing the equivalencies and similarities between curriculum standards in
different countries will allow content correlations to be reused between countries.


Task definition
---------------
Given a subset curriculum standards statements in Jurisdiction X (as set of standard nodes),
and a subset of the curriculum standards in Jurisdictions Y (another set of standard nodes),
discover all alignments between standard node, but identifying standards statements
that describe the same knowledge, competencies, or learning objectives.

**Inputs**: standards subsets `dx[subsetdx]` and `dy[subsetdy]`,
where `dx` is a ROC curriculum document defined in jurisdiction X,
and `dy` is a ROC curriculum document defined in jurisdiction Y.

**Outputs**: a list of `ContentStandardNodeRelation`s, `[ (sx, srkind, sy), ...]`
consisting of standard-to-standard links of type `drkind` between a subset of
the standards nodes specified in the inputs `dx[subsetdx]` and `dy[subsetdy]`.


Data
----
The following relevant ROC data is available for use for this task:
- Data from `StandardsDocument`s that consist of `StandardNode` trees
- Data from `StandardsCrosswalk`s consisting of `StandardNodeRelation` that
  define standard-to-standard alignments relations.
- Data from `ContentCollection`s that consist of `ContentNode` trees.
  There exist **O(100k)** content nodes organized into content collections like
  `khanadademy-en`, `kolibri-channel-ck12`, `kolibri-channel-ghana-math`, etc.
  Each content node has a title, description, source_url, and other metadata.
- Data from `StandardsDocument`s that consist of `StandardNode` trees.
  There exist **O(10)** jurisdictions (Brazil, Ghana, Honduras, Kenya, UK, USA, Zambia)
  for which curriculum standards documents are available in machine-readable form 
  and within each jurisdiction **O(10)** standards documents, with each document
  containing **O(100)** standard nodes. Each standard node has a description (str)
  that specifies a particular set of competencies expected of learners for a
  given grade level, within a particular academic subject.
  Standard nodes can be folder-like (intermediate levels of the hierarchy)
  or a atomic statements (leaf nodes).
- Existing content correlations `ContentCorrelation`s that consist of multiple
  content-to-standard links (`ContentStandardRelation`s) available in several
  jurisdictions (e.g. Khan Academy (`KA`) and Learning Equality `LE`).


Evaluation metrics
------------------
The "quality" of the output is measured using standard precision and recall
metrics evaluated against the ground truth provided by human experts
(a curriculum developer, alignment consultants, or other curriculum experts) who
produce standards crosswalk based on the same inputs `dx[subsetdx]` and `dy[subsetdy]`.
- Precision: what proportion of the `[(sx, srkind, sy), ...]` in the output were
  also identifier by human experts for same task.
- Recall: what proportion of the `[(sx, srkind, sy), ...]` identified by human
  experts are present in the output.


Challenges
----------
One concern/limitation about the overall goal of using standards crosswalks to
"port" content correlations data between different educational contexts, is the
"compounding of inaccuracy" aspect of alignment relations:
- If `(Lesson)--[lrmi:teaches]->(StdX.x)` is an 80% match,
  and `(StdX.x)--[asn:narrowAlignment]->(StdY.y)` is also 80% accurate,
  then the combined two-hop graph traversal will only be ~60% accurate.

This is why it's important to think about the semi-automated workflow strategies 
based on graph data as recommendations that need to be vetted by humans in the loop
(curriculum experts that know about the nuances of alignment work who can accept/reject
these recommendations). Still though, if we can use classical NLP and the latest
language models to give curriculum experts (and teachers, and learners) a 
"shortlist" of 10-100 content correlations recommendations based on the graph,
this will majorly improve their work (otherwise they have to wade through **O(100k)**
learning resources, and must fallback on generic keyword search tools, which are
known to have limitations for this task).



