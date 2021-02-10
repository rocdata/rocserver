Content correlations discovery
==============================
Automated content-standard link discovery (a.k.a content correlations).


Task CS definition
------------------
Given a subset of the content collections (imports from OER content repositories)
and a subset of curriculum standards statements (as set of standard nodes),
discover which content nodes are relevant for each standard node.

**Inputs**: content subset `cc1[subset1]` and standards subset `dx[subsetdx]`,
where `cc1` is some ROC data content collections, and `dx` is some ROC document.

**Outputs**: ContentStandardNodeRelation list: `[(ca, cskind, sx), ...]` consisting
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
The "objective quality" of the output can be measured using precision and recall
metrics evaluated against the "ground truth" content correlations produced by
human experts (curriculum experts, librarians, and educators) for same task of
identifying relevant correlations between content collection subset `cc1[subset1]`
and standards document subset `dx[subsetdx]`:
- **Precision**: what proportion of the `[(ca, cskind, sx), ...]` in the output were
  also identifier by human experts for same task.
- **Recall**: what proportion of the `[(ca, cskind, sx), ...]` identified by human
  experts are present in the output.


Challenges
----------
The problem of discovering correlated learning resources for standard nodes is
complicated by the following nuances of the task:

- A vocabulary gap exists between the language used in standard node descriptions
  and the language used in educational resources titles and descriptions.
  Standard node descriptions tend to be short, high-level abstract statements
  about what students should know, do, understand, etc. whereas learning resources
  use language relevant for concrete instances of these skills.
  This difference in conceptual level of the text descriptions makes it difficult
  to find commonalities between standard and resource when using "keyword match"
  techniques (same problem exists for manual alignment efforts based on search).
- Determining the "alignment" between a learning resource and a curriculum standard
  is a nuanced, context-dependent, and multi-faceted process. The catalogers
  working on content correlations must:
  - (S) know the curriculum standards, the cultural and pedagogical context
    of the teachers and learners who are the target users of the aligned-content
  - (C) know the content resources content, topics, and pedagogical approach,
    in order to make a correct judgement about the relevance and usefulness of
    each content resource to the target curriculum standards and educational context.
    The need for this "deep checks" for each content node is partially what
    makes the curriculum alignment task so time consuming.
