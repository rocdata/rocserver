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

The "objective quality" of the output can be measured using precision and recall
metrics evaluated against the "ground truth" content correlations produced by
human experts (curriculum experts, librarians, and educators):
 - Precision: what proportion of the `[(ca, cskind, sx), ...]` in the output were
   also identifier by human experts for same task `InferCS(cc1[subset1],dx[subsetdx])`.
 - Recall: what proportion of the `[(ca, cskind, sx), ...]` identified by human
   experts are present in the output.

We can further define "subjective quality" metrics to keep in mind which measure
the overall success of content-standard alignment task:
 - LANG FIT: are the resources available in the learner's language
 - FIT: are the resources a good fit for the target curriculum
 - CONTEXT FIT: appropriate and adapted to local culture, meets the needs of specific learners, and accessible.
 - COMPLETE: true if all topics are covered (i.e., no gaps)
 - COHERENT: is there narrative consistency 
 - MEASURABLE: when the content correlation includes assessment items that can be used to measure learning outcomes
 - APPROVED: true of linkage set has been approved by some certification body relevant to the context (e.g. local ministry).
 - SUPPORTED: teacher pedagogical training provided, examples of usage in lesson plans, continuously updated, sustainable
 - ENGAGING: the curriculum structure and content is interesting for the intended audience (not dry)

These qualitative metrics are of course more difficult to measure and verify in
the context of machine learning tasks, but it's important for machine learning
practitioners to be aware of the long term goal: making it easier for educators
and learners to find relevant learning resources, where the notion of relevance
is not just content or keyword match, but also pedagogical and contextual dimensions.



Challenges
----------

The problem of discovering correlated learning resources for standard nodes is
complicated by the following nuances of the task:
deceptively simple, but 

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
