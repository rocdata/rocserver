Roadmap
=======
This page lists various TODOs and next steps for the development of the ROC data
model and the `rocserver` application.


Standard node components
------------------------
Curriculum standard statements often contain additional information like:
- **Teaching time allocation**: guidance about how much class time to dedicate to
  each part of the curriculum
- **Teaching strategies / Suggested instructional methods**: similar to the above,
  but with suggestions targeting teachers
- **Content exemplars**: examples of text, images, equations, and formulas that
  illustrate the concepts students should be learning about
- **Content references**: reference to a specific textbooks or external learning resources
- **Suggested learning activities**: examples of recommended classroom activities
  that teachers can use to teach the given standard entry
- **Assessment notes**: description or examples of assessment items that can be
  used to evaluate a learner's knowledge on this standard entry
- **Connections to earlier entries in a progression**: vertical alignment information
- **Connections to other subjects in current grade**: horizontal alignment information
- **Practices / Core ideas / Cross-cutting concepts**: information about aspects
  of the curriculum that are not captured by the primary hierarchy of the document
- **Benchmarks / Rubrics**: specific criteria used to evaluate the attainment level
  of the competency described by the standard statement
- **Inquiry Questions**: key questions for organizing classroom discussions
- **Notes**: clarifications, additional information, and non-statutory guidance
  which can provide useful information about scope and emphasis

Standards documents also often contain sections with general information like:
- Notes about overall progressions between grades
- Cross-curricular competencies (e.g. problem solving, critical thinking)
- General outcomes for the whole educational program
- Values and principles of the educational system

These sections of the curriculum document can be very helpful for understanding
the standards since they provide the much needed interpretation context, however
these types of additional information differ widely between the standards in
different countries, so they have not been included in the initial work on the
ROC data model.

### Next steps
- Add an new model `StanrardNodeComponent` for storing additional information
  attached to any `StandardNode`. A standard component's `content` field must be
  able to support rich text features (formatted text, images, tables, equations, etc.).
  Each component has a different `kind` based a local controlled vocabulary.
- Update the web-browsing interface and data exports to display and include the
  standards components when displaying standard nodes.



Standard node sets
------------------
Within each standards document, we can identify subsets of the standards that
are relevant for educators teaching a course at a given grade level. Thinking
from the point of view of a teacher in charge of Grade 4 math in Country X,
the only info this teacher is interested in is the subset `Country X > Math > Grade 4`
and the topics and standards statements contained therein.
The standards for other grades are not relevant for their day-to-day activities
like preparation of course plans, lesson plans, and choosing learning resources
and teaching strategies to use with their students.

The top-levels of a standards document hierarchy are rarely meaningful and
documents in different countries follow can have different nesting structure.
Examples of hierarchies for the "core properties" (subject, grade level, topic)
include:
- `subject > grade level > topic`: a document whose sections describes standards
  for different subjects, with subsection corresponding to different grade levels,
  and subsubsections corresponding to educational topics (e.g. Algebra).
- `grade level > subject > topic`: a document subdivided by grade levels then
  by academic subject (e.g. Math), and topic (e.g. Algebra).
- `subject > topic > grade level`: a hierarchy in which a given topic appears at
  multiple grade levels.

In order to help teachers navigate the standards data, it would be helpful to
add "shortcuts" to specific subtrees of the standards document hierarchy,
each subset being described by a given (subject, grade levels, topic).
We will refer to these grade-level-, subject-, and topic-level subsets of a
standards document as `StandardSet`s. We can think of a standard set as a "symlink"
to a particular place within a standards document—a way to navigate standards document
that is most useful in practice for teachers, because they don't care about the
overall document, but only about a specific (grade level, subject, topic) subset.

A good example of such teacher-first organizational structure can be seen in the
[mapping](https://github.com/commonstandardsproject/api/blob/master/importer/matchers/source_to_subject_mapping_grouped.rb#L104-L134) performed by the importer scripts
of the [common standards project](https://commonstandardsproject.com), which
process source documents and organize them into standard sets useful for teachers.

### Use cases for standard sets
- As a teacher, I can easily drill-down to the subset of a standards document
  relevant for my needs.
- Identify meaningful subsets of standards documents to use for human-powered
  digitization and curriculum alignment efforts (multiple curriculum experts
  working in parallel on different subsets of a document). The same subsets can
  also be used for [automation](./automation/index.html) workflows.
- Different versions of curriculum standards are identified by including the year
  of publication in the `StandardSet` title, e.g. `Kenya, Math, Grade 4 (2002)`
  (the old standards) vs. `Kenya, Math, Grade 4 (2019)` (the new CBC standards).
- Educators can easily find a list of all standards sets for a particular grade
  level (e.g. a teacher looking to add cross-curriculum links in their lessons).


### Next steps
- Add the `StandardSet` model that "points" to a `StandardsDocument` and a 
  `StandardNode` within that document.
- Update the standards document web-browsing interface and data exports to
  display standard sets shortcuts.




Search
------
Frontend applications based on the `rocdata.global` web service would benefit
from access to a search interface for standards documents, standard nodes,
content nodes, and the relations between them (content correlations and standards crosswalks).

### Next steps
- Implement search functionality through a new endpoint
- Provide sample code for using search endpoint
- (stretch goal) Implement fulltext search within content nodes

