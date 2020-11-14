##################################################
# MIT License
#
# Copyright (c) 2019 Learning Equality
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
##################################################


import os
import zipfile

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from treebeard.mp_tree import MP_Node





# CURRICULUM DOCUMENTS
################################################################################

DIGITIZATION_METHODS = [
    ("manual_entry", "Manual data entry"),
    ("scan_manual", "Curriculum manually extracted from OCR"),
    ("automated_scan", "Automated stucture extraction via OCR"),
    ("website_scrape", "Curriculum scraped from website"),
    ("data_import", "Curriculum imported from data"),
]


class CurriculumDocument(models.Model):
    """
    Stores the metadata for a curriculum document, e.g. KICD standards for math.
    """

    # id = auto-incrementing integet primary key
    source_id = models.CharField(
        unique=True,
        max_length=200,
        help_text="A unique identifier for the source document",
    )
    title = models.CharField(max_length=200)
    country = models.CharField(max_length=200, help_text="Country")
    digitization_method = models.CharField(
        choices=DIGITIZATION_METHODS, max_length=200, help_text="Digitization method"
    )
    source_url = models.CharField(
        max_length=200, blank=True, help_text="URL of source used for this document"
    )
    # root = reverse relation on StandardNode.document
    created = models.DateTimeField(auto_now_add=True)
    # ? modified = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(
        default=True, help_text="True for draft version of the curriculum data."
    )
    official = models.BooleanField(
        default=False, help_text="Curriculum document is an official national standard"
    )

    @property
    def root(self):
        return StandardNode.get_root_nodes().get(document=self)

    def __str__(self):
        return "{}: {} ({})".format(self.country, self.title, self.source_id)


def overwriting_file_upload_name(section, filename):
    """
    Ensure section_zip files uploaded preserve their original name.
    """
    path = os.path.join(settings.UPLOADS_ROOT, filename)
    if os.path.exists(path):
        os.remove(path)
    return path



# CURRICULUM DATA
################################################################################


class StandardNode(MP_Node):
    """
    The individual elements of a curriculum structure.
    """

    # id = auto-incrementing integet primary key
    # path = inherited from MP_Node, e.g. ['0001'] for root node of tree_id 0001
    document = models.ForeignKey(
        "CurriculumDocument", related_name="nodes", on_delete=models.CASCADE
    )
    identifier = models.CharField(max_length=300)
    # source_id / source_url ?
    kind = models.CharField(max_length=100)
    title = models.TextField(help_text="Primary text that represents this node.")
    # the order of tree children within parent node
    sort_order = models.FloatField(default=1.0)
    node_order_by = ["sort_order"]

    # domain-specific
    time_units = models.FloatField(
        blank=True,
        null=True,
        help_text="A numeric value ~= to the # hours of instruction for this unit or topic",
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes, description, and supporting text from the source.",
    )
    # basic model extensibility w/o changing base API
    extra_fields = JSONField(default=dict)

    # Human relevance jugments on edges between nodes
    @property
    def judgments(self):
        return HumanRelevanceJudgment.objects.filter(Q(node1=self) | Q(node2=self))

    def __str__(self):
        return "{} {}".format(self.identifier, self.title)

    def add_child(self, **kwargs):
        if "document" not in kwargs:
            kwargs["document"] = self.document
        return super().add_child(**kwargs)

    def get_earlier_siblings(self):
        return self.get_siblings().filter(sort_order__lt=self.sort_order)

    def get_later_siblings(self):
        return self.get_siblings().filter(sort_order__gt=self.sort_order)

    class Meta:
        constraints = [
            UniqueConstraint(  # Make sure every document has at most one tree
                name="single_root_per_document",
                fields=["document", "depth"],
                condition=Q(depth=1),
            )
        ]


# HUMAN JUDGMENTS
################################################################################


class HumanRelevanceJudgment(models.Model):
    """
    Stores human feedback about relevance for an `AlignmentEdge` between two nodes.
    Relevance edges are stored as directed edges but are logically undirected.
    """

    # id = auto-incrementing integet primary key
    node1 = models.ForeignKey(
        StandardNode, related_name="node1+", on_delete=models.CASCADE
    )
    node2 = models.ForeignKey(
        StandardNode, related_name="node2+", on_delete=models.CASCADE
    )

    # Relevnace rating: min = 0.0 (not relevant at all), max = 1.0 (highly relevant)
    rating = models.FloatField(blank=True, null=True)
    # Optional confidence level: 1.0= 100% sure, 50% depends, 0% just guessing
    confidence = models.FloatField(blank=True, null=True)
    extra_fields = JSONField(default=dict)

    mode = models.CharField(max_length=30)  # manually added vs. rapid feedback
    # Save the info about the UI frontend used to provide judgment (team name)
    ui_name = models.CharField(max_length=100)
    ui_version_hash = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="judgments",
        null=True,
        on_delete=models.SET_NULL,
    )
    created = models.DateTimeField(auto_now_add=True)
    is_test_data = models.BooleanField(
        blank=True, null=True, help_text="True for held out test data."
    )

    def __str__(self):
        return "{} <--{}--> {}".format(
            repr(self.node1_id), self.rating, repr(self.node2_id)
        )





# SCANNED DOCUMENT SECTIONS
################################################################################

class DocumentSection(MP_Node):
    document = models.ForeignKey(
        "CurriculumDocument", related_name="chunks", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    section_zip = models.FileField(
        null=True, blank=True, upload_to=overwriting_file_upload_name
    )
    num_chunks = models.IntegerField(default=0)
    text = models.TextField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="section_reviews",
    )
    is_draft = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_section_for_review(cls):
        # make sure we return an item that has a file associated with it, and has not had a review session yet.
        return (
            cls.objects.filter(reviewed_by=None)
            .exclude(section_zip="")
            .exclude(section_zip=None)
            .first()
        )

    def get_section_dir(self):
        """
        Gets the directory to store files in based on the document's hierarchy.

        :return: String path to directory if this node has a section_zip file, None otherwise.
        """
        if self.section_zip:
            dir_names = [self.name]
            parent = self.get_parent()
            while parent:
                dir_names.insert(0, parent.name)
                parent = parent.get_parent()
            if self.document:
                dir_names.insert(0, self.document.source_id)
            rel_path = os.path.sep.join(dir_names)
            return rel_path

        return None

    def save(self, *args, **kwargs):
        super(DocumentSection, self).save(
            *args, **kwargs
        )  # pre-save to process self.section_zip
        if self.section_zip:
            rel_path = self.get_section_dir()
            full_path = os.path.join(settings.SCANS_ROOT, rel_path)
            text_path = os.path.join(full_path, "{}_combined.txt".format(self.name))
            if not os.path.exists(text_path):
                os.makedirs(full_path, exist_ok=True)

                zip = zipfile.ZipFile(self.section_zip.path)
                zip.extractall(full_path)
                zip.close()

            if not self.text or len(self.text) == 0:
                text = open(text_path, "r", encoding="utf-8").read()
                # convert line breaks to new paragraphs to ease cleanup.
                self.text = "<p>{}</p>".format(
                    text.replace("\r", "").replace("\n", "</p><p>")
                )

                super(DocumentSection, self).save(*args, **kwargs)

    class Meta:
        constraints = [
            UniqueConstraint(  # Make sure every document has at most one tree
                name="document_section_single_root",
                fields=["document", "depth"],
                condition=Q(depth=1),
            )
        ]



# USER PROFILES
################################################################################

BACKGROUNDS = [
    ("instructional_designer", "Instructional Designer"),
    ("curriculum", "Curriculum Alignment Expert"),
    ("content_expert", "OER Expert"),
    ("teacher", "Teacher/Coach"),
    ("designer", "Designer or Frontend Developer"),
    ("developer", "Technologist and/or Developer"),
    ("data_science", "Machine Learning and Data Science"),
    ("metadata", "Metadata"),
    ("other", "Other"),
]


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    background = models.CharField(
        max_length=50,
        choices=BACKGROUNDS,
        help_text="What is your background experience?",
    )
    subject_areas = models.ManyToManyField(
        to="alignmentapp.SubjectArea", related_name="user_profiles", blank=True
    )
    exclude = models.BooleanField(default=False)

    def __str__(self):
        return "Profile for {}".format(self.user.username)


class SubjectArea(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# CURRICULUM DOCUMENTS
################################################################################

DIGITIZATION_METHODS = [
    ("manual_entry", "Manual data entry"),
    ("scan_manual", "Curriculum manually extracted from OCR"),
    ("automated_scan", "Automated stucture extraction via OCR"),
    ("website_scrape", "Curriculum scraped from website"),
    ("data_import", "Curriculum imported from data"),
]


class CurriculumDocument(models.Model):
    """
    Stores the metadata for a curriculum document, e.g. KICD standards for math.
    """

    # id = auto-incrementing integet primary key
    source_id = models.CharField(
        unique=True,
        max_length=200,
        help_text="A unique identifier for the source document",
    )
    title = models.CharField(max_length=200)
    country = models.CharField(max_length=200, help_text="Country")
    digitization_method = models.CharField(
        choices=DIGITIZATION_METHODS, max_length=200, help_text="Digitization method"
    )
    source_url = models.CharField(
        max_length=200, blank=True, help_text="URL of source used for this document"
    )
    # root = reverse relation on StandardNode.document
    created = models.DateTimeField(auto_now_add=True)
    # ? modified = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(
        default=True, help_text="True for draft version of the curriculum data."
    )
    official = models.BooleanField(
        default=False, help_text="Curriculum document is an official national standard"
    )

    @property
    def root(self):
        return StandardNode.get_root_nodes().get(document=self)

    def __str__(self):
        return "{}: {} ({})".format(self.country, self.title, self.source_id)


def overwriting_file_upload_name(section, filename):
    """
    Ensure section_zip files uploaded preserve their original name.
    """
    path = os.path.join(settings.UPLOADS_ROOT, filename)
    if os.path.exists(path):
        os.remove(path)
    return path


class DocumentSection(MP_Node):
    document = models.ForeignKey(
        "CurriculumDocument", related_name="chunks", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    section_zip = models.FileField(
        null=True, blank=True, upload_to=overwriting_file_upload_name
    )
    num_chunks = models.IntegerField(default=0)
    text = models.TextField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="section_reviews",
    )
    is_draft = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_section_for_review(cls):
        # make sure we return an item that has a file associated with it, and has not had a review session yet.
        return (
            cls.objects.filter(reviewed_by=None)
            .exclude(section_zip="")
            .exclude(section_zip=None)
            .first()
        )

    def get_section_dir(self):
        """
        Gets the directory to store files in based on the document's hierarchy.

        :return: String path to directory if this node has a section_zip file, None otherwise.
        """
        if self.section_zip:
            dir_names = [self.name]
            parent = self.get_parent()
            while parent:
                dir_names.insert(0, parent.name)
                parent = parent.get_parent()
            if self.document:
                dir_names.insert(0, self.document.source_id)
            rel_path = os.path.sep.join(dir_names)
            return rel_path

        return None

    def save(self, *args, **kwargs):
        super(DocumentSection, self).save(
            *args, **kwargs
        )  # pre-save to process self.section_zip
        if self.section_zip:
            rel_path = self.get_section_dir()
            full_path = os.path.join(settings.SCANS_ROOT, rel_path)
            text_path = os.path.join(full_path, "{}_combined.txt".format(self.name))
            if not os.path.exists(text_path):
                os.makedirs(full_path, exist_ok=True)

                zip = zipfile.ZipFile(self.section_zip.path)
                zip.extractall(full_path)
                zip.close()

            if not self.text or len(self.text) == 0:
                text = open(text_path, "r", encoding="utf-8").read()
                # convert line breaks to new paragraphs to ease cleanup.
                self.text = "<p>{}</p>".format(
                    text.replace("\r", "").replace("\n", "</p><p>")
                )

                super(DocumentSection, self).save(*args, **kwargs)

    class Meta:
        constraints = [
            UniqueConstraint(  # Make sure every document has at most one tree
                name="document_section_single_root",
                fields=["document", "depth"],
                condition=Q(depth=1),
            )
        ]



# MACHINE LEARNING
################################################################################


class Parameter(models.Model):
    """
    General-purpse key-value store. Used to store:
      - test_size (float-compatible str): proportion of human judgments to set
        aside for use as the testing set.
    """

    key = models.CharField(max_length=200, unique=True)
    value = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class DataExport(models.Model):
    """
    Keep track when data exports was done and which folder it was saved to.
    """

    exportdirname = models.CharField(max_length=400, blank=True, null=True)
    started = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(blank=True, null=True)


# CAMPAIGNS
################################################################################

# ACTIONS = [
#     ("reviewed_section", "Reviewed Curriculum Document Section"),
#     ("submitted_judgment", "Submitted Human Judgment"),
# ]


class Campaign(models.Model):
    """
    Campaigns set a particular goal, such as adding human judgments or doing curriculum document cleanup.
    While we may eventually want to have more sophisticated tracking, in this initial version, a
    campaign will have a start and end date, a target number of actions to complete, and both a base point
    value along with a completion reward.

    Example:
        "Add 500 new human judgments to the database. Points: 5 per judgment, Completion bonus: 100 points"

    Current progress can be calculated by checking all `UserActions` in the database that match the campaign and
    happened between `start` and `end` time, then dividing the count by the `target_num`.

    Leaderboards can be shown by adding up the points of each user who participated in the campaign.
    """

    title = models.CharField(max_length=200)
    type = models.CharField(max_length=100)
    target_num = models.IntegerField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    completed = models.BooleanField(default=False)
    point_value = models.IntegerField()
    completion_points = models.IntegerField()

    def handle_campaign_completed(self):
        self.completed = True
        self.save()
        # TODO: add completion_bonus UserAction valued at self.completion_points to all users who contributed

    def get_campaign_progress(self):
        actions = UserAction.objects.filter(Q(campaign=self) | Q(type=self.type))
        if actions.count() >= self.target_num and not self.completed:
            self.handle_campaign_completed()
        percent = actions.count() / self.target_num
        return max(percent, 1) * 100


class UserAction(models.Model):
    """
    A user action is a record of an action performed by a user that awards points.
    While actions can be connected to campaigns, not all actions must be part of a campaign.
    (e.g. we could award points for registration, or filling out the profile, etc.)

    Action should be a string ID for a specific action performed, e.g. profile_completed, and we should
    keep a record of all possible actions and their point values. (In the db?)
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="actions", on_delete=models.CASCADE
    )
    # if a campaign gets deleted at some point, make sure people don't wake up to missing points!
    campaign = models.ForeignKey(
        "Campaign",
        null=True,
        blank=True,
        related_name="actions",
        on_delete=models.SET_NULL,
    )
    action = models.CharField(max_length=100)
    points = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}: {} ({} points, {})".format(
            self.user.username, self.action, self.points, self.timestamp
        )


# SIGNALS
################################################################################


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Make sure we auto-create an auth token for the user qwhenever a new user is created.
    """
    if created:
        Token.objects.create(user=instance)
