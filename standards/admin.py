from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from mptt.admin import DraggableMPTTAdmin

from standards.models import Jurisdiction, UserProfile
from standards.models import ControlledVocabulary, Term, TermRelation
from standards.models import StandardsDocument, StandardNode





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
