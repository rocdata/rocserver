Machine learning tasks
======================
This document describes machine learning tasks inference metadata discovery tasks
based on ROC data available thorough [rocdata.global](https://rocdata.global).

The end-goal to be able to categorize educational resources (content collections)
according to their relevance for local curriculum standards (standards nodes).
You can think of the end-user as a teacher in country X that needs to find relevant
learning resources and create a lesson. Starting from a un-categorized collection
of learning resources is too time consuming and difficult, but if the same resources
are categorized according to the local curriculums standards of country X, then
the teacher will find relevant resources much more easily.


Tasks
-----
We have identified two specific tasks (ML challenges) related to the overall goal:

 - [Content correlations discovery](./content_correlations_discovery.md)
 - [Standards crosswalk discovery](./standards_crosswalk_discovery.md)



Prior work
----------
The links below represent a non-exhaustive list of ML research related to the
general domain of automated discovery of content correlations and standards crosswalks:
- 2010: The paper "Computer-Assisted Assignment of Educational Standards Using
  Natural Language Processing" by Devaul, Diekema, and Ostwald describes an
  approach for a cataloging tool that aids catalogers in the assignment of
  standards metadata to digital library resources based on natural language
  processing techniques.
- 2017-2019: multiple consultations and events including educators, curriculum designers,
  ministries of education, platform developers, machine learning experts,
  and other key stakeholders from the educational domain with a common interest
  to make relevant learning resources accessible to teachers and learners in low-resource contexts. 
- October 2019: the San Francisco hackathon on automation of curriculum alignment
  was held that included a prototypes of standards crosswalks discovery task.
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
  and defines data model for curriculum documents, content correlations data,
  and standards crosswalks data.



Get involved
------------
All datasets and models developed as part of this collaboration have been released
as public goods (open source) on [GitHub](https://github.com/rocdata).
Feel free to explore the available data, and code samples, and be on the lookout
for ML challenges and organized events in the coming year.
