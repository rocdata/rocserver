Content correlations discovery
==============================
Automated content-standard link discovery (a.k.a content correlations).


Task CS definition
------------------
Given a subset of the content collections (imports from OER content repositories)
and a subset of curriculum standards statements (as set of standard nodes),
discover which content nodes are relevant for each standard node.

**Inputs:** content subset: `cc1[subset1]` and standards subset `dx[subsetdx]`,
where `cc1` is some ROC data content collections, and `dx` is some ROC document.

**Outputs:** ContentStandardNodeRelation list: `[(ca, cskind, sx), ...]` consisting
of content-to-standard links of type `csking` between subset of standards and the 
subset of content nodes specified in the input.



Data
----

The following relevant ROC data is available for use with this task:

 - Data from `ContentCollection`s that consist of `ContentNode` trees.
   There exist **O(100k)** content nodes organized into content collections like
   `khanadademy-en`, `kolibri-channel-ck12`, `kolibri-channel-ghana-math`, etc.
   Each content node has a title, description, source_url, and other metadata.
 - Data from `StandardsDocument`s that consist of `StandardNode` trees.
   There exist **O(10)** jurisdictions (Brazil, Ghana, Honduras, Kenya, UK, USA, Zambia)
   for which curriculum standards documents are available in machine-readable form 
   and within each jurisdiction O(10) standards documents, with each document
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
The "quality" of the output is measured using standard
precision and recall metrics evaluated against the ground truth provided by
human experts (curriculum experts, librarians, and educators):
 - Precision: what proportion of the `[(ca, cskind, sx), ...]` in the output were
   also identifier by human experts for same task `InferCS(cc1[subset1],dx[subsetdx])`.
 - Recall: what proportion of the `[(ca, cskind, sx), ...]` identified by human
   experts are present in the output.


