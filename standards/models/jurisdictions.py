from django.conf import settings
from django.db.models import CASCADE
from django.db.models import CharField
from django.db.models import ForeignKey
from django.db.models import OneToOneField
from django.db.models import Manager
from django.db.models import Model
from django.db.models import TextField
from django.db.models import URLField
from django_countries.fields import CountryField
from standards.fields import ShortUUIDField





# JURISDICTIONS and USERS
################################################################################


class JurisdictionManager(Manager):

    def get_by_natural_key(self, name):
        return self.get(name=name)


class Jurisdiction(Model):
    """
    The top-level organizational structure in which the standards documents are
    published, promulgated. Institutions that publish standards include ministries,
    curriculum bodies, an assessment boards, professional organizations, etc.
    """
    id = ShortUUIDField(primary_key=True, editable=False, prefix='J')
    # data
    display_name = CharField(max_length=200, help_text="Official name of the organization or government body")
    name = CharField(max_length=200, unique=True, help_text="the name used in URIs")
    country = CountryField(blank=True, null=True, help_text='Country of jurisdiction')
    alt_name = CharField(max_length=200, blank=True, null=True, help_text="Alternative name")
    language = CharField(max_length=20, blank=True, null=True, help_text="BCP47 lang codes like en, es, fr-CA")
    notes = TextField(blank=True, null=True, help_text="Public comments and notes about this jurisdiction.")
    website_url = URLField(max_length=512, null=True, blank=True)

    objects = JurisdictionManager()

    def natural_key(self):
        return (self.name,)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/terms/" + self.name

    @property
    def uri(self):
        return self.get_absolute_url()


class UserProfile(Model):
    user = OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name="profile")
    background = CharField(max_length=200, help_text="What is your background?")
    jurisdiction = ForeignKey(Jurisdiction, related_name="userprofiles", on_delete=CASCADE)
    # roles within a jurisdiction are: admin/editor/approver/technical

    def __str__(self):
        return self.user.username + ' (email=' + self.user.email +')'



