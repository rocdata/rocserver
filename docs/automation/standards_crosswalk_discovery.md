Standards crosswalk discovery
=============================

Task definition
---------------
Given a subset curriculum standards statements in Jurisdiction X (as set of standard nodes),
and a subset of the curriculum standards in Jurisdictions Y (another set of standard nodes),
discover all alignments between standard node, but identifying standards statements
that describe the same knowledge, competencies, or learning objectives.

**Inputs:** standards subsets `dx[subsetdx]` and `dy[subsetdy]`,
where `dx` is a ROC curriculum document defined in jurisdiction X,
and `dy` is a ROC curriculum document defined in jurisdiction Y.

**Outputs:** a list of `ContentStandardNodeRelation`s: `[ (sx, srkind, sy), ...]`
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
The "quality" of the output is measured using standard precision and recall metrics
evaluated against the ground truth provided by human experts (representatives from
ministries of education, curriculum developers, etc.):
 - Precision: what proportion of the `[(sx, srkind, sy), ...]` in the output were
   also identifier by human experts for same task `InferSC(dx[subsetdx],dy[subsetdy])`.
 - Recall: what proportion of the `[(sx, srkind, sy), ...]` identified by human
   experts are present in the output.

