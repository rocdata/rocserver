Machine learning tasks
======================
This document describes machine learning tasks inference metadata discovery tasks
based on ROC data: [rocdata.global](https://rocdata.global).

The end-goal to be able to categorize educational resources (content collections)
according to their relevance for local curriculum standards (standards nodes).
You can think of the end-user as a teacher in country X that needs to find relevant
learning resources and create a lesson. Starting from a un-categorized collection
of learning resources is too time consuming and difficult, but if the same resources
are categorized according to the local curriculums standards of country X, then
the teacher will find relevant resources much more easily.



## Task CS: automated content-standard link discovery (a.k.a content correlations)

Given a subset of the content collections (imports from OER content repositories)
and a subset of curriculum standards statements (as set of standard nodes),
discover which content nodes are relevant for each standard node.

**Inputs:** content subset: `cc1[subset1]` and standards subset `dx[subsetdx]`,
where `cc1` is some ROC data content collections, and `dx` is some ROC document.

**Outputs:** ContentStandardNodeRelation list: `[(ca, cskind, sx), ...]` consisting
of content-to-standard links of type `csking` between subset of standards and the 
subset of content nodes specified in the input.

**Data:** The following relevant ROC data is available for use with this task:
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

**Evaluation metrics:** The "quality" of the output is measured using standard
precision and recall metrics evaluated against the ground truth provided by
human experts (curriculum experts, librarians, and educators):
 - Precision: what proportion of the `[(ca, cskind, sx), ...]` in the output were
   also identifier by human experts for same task `InferCS(cc1[subset1],dx[subsetdx])`.
 - Recall: what proportion of the `[(ca, cskind, sx), ...]` identified by human
   experts are present in the output.



## Task SC: automated discovery of standards crosswalks

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

**Data:** The following relevant ROC data is available for use for this task:
 - Data from `StandardsDocument`s that consist of `StandardNode` trees
 - Data from `StandardsCrosswalk`s consisting of `StandardNodeRelation` that
   define standard-to-standard alignments relations.

**Evaluation metrics:** The "quality" of the output is measured using standard
precision and recall metrics evaluated against the ground truth provided by
human experts (ministries of education, curriculum developers, etc.):
 - Precision: what proportion of the `[(sx, srkind, sy), ...]` in the output were
   also identifier by human experts for same task `InferSC(dx[subsetdx],dy[subsetdy])`.
 - Recall: what proportion of the `[(sx, srkind, sy), ...]` identified by human
   experts are present in the output.




## Prior work

The links below represent a non-exhaustive list of ML research related to ROC data:
 - 2017-2019: multiple consultations and events inluding educators, curriculum designers,
   ministries of education, platform developers, machine learning experts,
   and other key stakeholders from the educational domain with a common interest
   to make relevant learning resources accessible to teachers and learners in low-resource contexts. 
 - October 2019: the San Francisco hackathon on automation of curriculum alignment
   was held that included a prototypes of `Task  SC`. The hackathon is part of
   Read the [hackathon report](https://learningequality.org/r/hackathon-oct19-report)
   for additional info and links to relevant GitHub repositories,
   [watch the video](https://learningequality.org/r/hackathon-oct19-video),
   and [learn about participants' reflections](https://blog.learningequality.org/hackathon19-debrief-7f1911d9b109).
    - Starter code:
    - Example colab notebook:
    - Human-judgment user interfaces:
    - Related-standards browsing interfaces:
 - January 2021: ROC data report "Digitizing Curriculum Standards to Unlock the
   Potential of Open Educational Resources in a Global Context," which outlines
   the use cases for digital curriculum standards for a non-technical audience,
   and defines data model for curriculum documents, content correlations data 
   (outputs of `Task CS`), and standards crosswalks data (outputs of `Task SC`).



## Get involved

All datasets and models developed as part of this collaboration have been released
as public goods (open source) on [GitHub](https://github.com/rocdata).
Feel free to explore the available data, and code samples, and be on the lookout
for ML challenges and organized events in the coming year.

