from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from mptt.admin import DraggableMPTTAdmin

from standards.models import Jurisdiction, UserProfile
from standards.models import ControlledVocabulary, Term, TermRelation
from standards.models import StandardsDocument, StandardNode
from standards.models import StandardsCrosswalk, StandardNodeRelation
from standards.models import ContentCollection, ContentNode, ContentNodeRelation
from standards.models import ContentCorrelation, ContentStandardRelation



# JURISDICTIONS and USERS
################################################################################

@admin.register(Jurisdiction)
class JurisdictionAdmin(admin.ModelAdmin):
    list_display = ["name",  "display_name", "country", "id"]
    list_filter = ("country", "language")
    search_fields = ["id", "name", "display_name", "alt_name", "notes"]
    model = Jurisdiction

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile




# CONTROLLED VOCABULARIES
################################################################################

@admin.register(ControlledVocabulary)
class ControlledVocabularyAdmin(admin.ModelAdmin):
    list_display = ["name", "kind", "label", "jurisdiction", "id", "date_created", "date_modified"]
    list_filter = ("jurisdiction", "language")
    search_fields = ["id", "name", "label", "alt_label", "hidden_label", "description", "notes"]
    model = ControlledVocabulary


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ["vocabulary", "path", "label", "notation", "language", "id", "date_created", "date_modified"]
    list_filter = ("vocabulary", "language")
    search_fields = ["id", "path", "label", "alt_label", "hidden_label", "notation", "definition", "notes"]
    model = Term


@admin.register(TermRelation)
class TermRelationAdmin(admin.ModelAdmin):
    list_display = ["id", "source", "kind", "target_uri", "target", "date_created", "date_modified"]
    list_filter = ("kind", "source", "target", "target_uri")
    search_fields = ["id", "path", "label", "alt_label", "hidden_label", "notation", "definition", "notes"]
    readonly_fields = ["id"]
    model = TermRelation




# CURRICULUM STANDARDS
################################################################################

@admin.register(StandardsDocument)
class StandardsDocumentAdmin(admin.ModelAdmin):
    list_display = ["name", "id", "jurisdiction", "title", "version", "publication_status", "digitization_method"]
    list_filter = ("jurisdiction", "publication_status", "subjects")
    search_fields = ["id", "title", "name", "description", "publisher", "notes"]
    readonly_fields = ["id"]
    model = StandardsDocument


@admin.register(StandardNode)
class StandardNodeAdmin(DraggableMPTTAdmin):
    list_display = ["tree_actions", "indented_title", "notation", "list_id", "title"]
    list_display_links=["indented_title",]
    list_filter = ("document__jurisdiction", "document", "kind", "language", "concept_keywords")
    search_fields = ["id", "notation", "title", "description", "concept_keywords", "notes", "extra_fields"]
    readonly_fields = ["id"]



# STANDARDS CROSSWALKS
################################################################################

@admin.register(StandardsCrosswalk)
class StandardsCrosswalkAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "digitization_method", "jurisdiction"]
    list_filter = ("jurisdiction", "digitization_method", "subjects", "education_levels")
    readonly_fields = ["id"]


@admin.register(StandardNodeRelation)
class StandardNodeRelationAdmin(admin.ModelAdmin):
    list_display = ["id", "source", "kind", "target"]
    raw_id_fields = ("source", "target",)
    list_filter = ("crosswalk__jurisdiction", "crosswalk", "kind", "crosswalk__subjects", "crosswalk__education_levels")
    readonly_fields = ["id"]





# CONTENT
################################################################################

@admin.register(ContentCollection)
class ContentCollectionAdmin(admin.ModelAdmin):
    list_display = ["name", "id", "jurisdiction", "collection_id", "version", "publication_status"]
    list_filter = ("jurisdiction", "publication_status", "subjects")
    search_fields = ["id", "name", "description", "notes"]
    readonly_fields = ["id"]
    model = ContentCollection


@admin.register(ContentNode)
class ContentNodeAdmin(DraggableMPTTAdmin):
    list_display = ["tree_actions", "indented_title", "source_id"]
    list_display_links=["indented_title",]
    raw_id_fields = ("parent",)
    list_filter = ("collection", "kind", "language", "concept_keywords")
    search_fields = ["id", "title", "description", "concept_keywords", "notes", "extra_fields"]
    readonly_fields = ["id"]
    expand_tree_by_default = False


@admin.register(ContentNodeRelation)
class ContentNodeRelationAdmin(admin.ModelAdmin):
    list_display = ["id", "source", "kind", "target", "date_modified"]
    raw_id_fields = ("source", "target",)
    list_filter = ("kind", "source", "target")
    readonly_fields = ["id"]
    model = ContentNodeRelation




# CONTENT CORRELATIONS
################################################################################

@admin.register(ContentCorrelation)
class ContentCorrelationAdmin(admin.ModelAdmin):
    list_display = ["title", "id", "jurisdiction", "version", "publication_status"]
    list_filter = ("jurisdiction", "publication_status", "subjects", "education_levels")
    readonly_fields = ["id"]
    model = ContentCorrelation


@admin.register(ContentStandardRelation)
class ContentStandardRelationAdmin(admin.ModelAdmin):
    list_display = ["id", "correlation", "contentnode", "kind", "standardnode", "date_modified"]
    raw_id_fields = ("contentnode", "standardnode",)
    list_filter = ("correlation", "kind")
    readonly_fields = ["id"]
    model = ContentStandardRelation




