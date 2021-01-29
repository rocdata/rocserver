"""
The ``standards-server`` URL configuration file.

"""

from django.conf import settings
from django.urls import path, include, re_path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_nested import routers


# Each API endpoint returns either HTML or JSON depending on the request accept
# headers. Alternatively an extension can be added to force a particular format.
ALLOWED_FORMATS = ["html", "json"]
ALLOWED_FORMATS_SUFFIX = "\.(?P<format>(%s))" % "|".join(ALLOWED_FORMATS)



# WEBSITE
################################################################################

from website.views import index, homepage, page

urlpatterns = [
    path('', index, name='index'),
    path('pages/', homepage, name='homepage'),
    path('pages/<val>/', page, name='page'),
    # tmp fallback
    path('pages', homepage, name='homepage-noslash'),
    path('pages/<val>', page, name='page-noslash'),
]


# JURISDICTIONS
################################################################################
from standards.api import JurisdictionViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'', JurisdictionViewSet)
jurisdiction_router = routers.NestedSimpleRouter(router, r'', lookup='jurisdiction', trailing_slash=False)



# VOCABULARIES and TERM RELATIONS
################################################################################

from standards.api import ControlledVocabularyViewSet, TermRelationViewSet

jurisdiction_router.register(r'terms', ControlledVocabularyViewSet, basename='jurisdiction-vocabulary')
jurisdiction_router.register(r'termrels', TermRelationViewSet, basename='jurisdiction-termrelation')


# TERMS
################################################################################

from standards.api import TermViewSet

juri_vocab_term_list = TermViewSet.as_view({
    'get': 'list',
    'post': 'create',
}, detail=False, suffix="List")

juri_vocab_term_detail = TermViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
}, detail=True, suffix="Instance")

# Term LIST+CREATE
# We wire up /{juri}/terms/{vocab.name}/ manually to get the list behavior that
# doesn't interfere with the vocab. detail endpoint /{juri}/terms/{vocab.name}
urlpatterns += [
    re_path(
        r'^(?P<jurisdiction_name>[\w_\-]*)/terms/(?P<vocabulary_name>[\w_\-]*)/$',
        juri_vocab_term_list,
        name='jurisdiction-vocabulary-term-list'
    ),
    re_path(
        r'^(?P<jurisdiction_name>[\w_\-]*)/terms/(?P<vocabulary_name>[\w_\-]*)/%s$' % ALLOWED_FORMATS_SUFFIX,
        juri_vocab_term_list,
        name='jurisdiction-vocabulary-term-list-with-format-suffix'
    ),
]

# Term DETAIL
# We wire up /{juri}/terms/{vocab.name}/{term.path} manually because the default
# behavior of drf-nested-routers introduces an extra slash ..//{term.path}.
urlpatterns += format_suffix_patterns([
    re_path(
        r'^(?P<jurisdiction_name>[\w_\-]*)/terms/(?P<vocabulary_name>[\w_\-]*)/(?P<path>[\w/_\-]*)$',
        juri_vocab_term_detail,
        name='jurisdiction-vocabulary-term-detail'
    ),
], allowed=ALLOWED_FORMATS)



# STANDARDS
################################################################################

from standards.api import StandardsDocumentViewSet, StandardNodeViewSet
from standards.api import StandardsCrosswalkViewSet, StandardNodeRelationViewSet

jurisdiction_router.register(r'documents', StandardsDocumentViewSet, basename='jurisdiction-document')
jurisdiction_router.register(r'standardnodes', StandardNodeViewSet, basename='jurisdiction-standardnode')
jurisdiction_router.register(r'standardscrosswalks', StandardsCrosswalkViewSet, basename='jurisdiction-standardscrosswalk')
jurisdiction_router.register(r'standardnoderels', StandardNodeRelationViewSet, basename='jurisdiction-standardnoderel')



# CONTENT
################################################################################

from standards.api import ContentCollectionViewSet, ContentNodeViewSet, ContentNodeRelationViewSet
from standards.api import ContentCorrelationViewSet, ContentStandardRelationViewSet

jurisdiction_router.register(r'contentcollections', ContentCollectionViewSet, basename='jurisdiction-contentcollection')
jurisdiction_router.register(r'contentnodes', ContentNodeViewSet, basename='jurisdiction-contentnode')
jurisdiction_router.register(r'contentnoderels', ContentNodeRelationViewSet, basename='jurisdiction-contentnoderel')
jurisdiction_router.register(r'contentcorrelations', ContentCorrelationViewSet, basename='jurisdiction-contentcorrelation')
jurisdiction_router.register(r'contentstandardrels', ContentStandardRelationViewSet, basename='jurisdiction-contentstandardrel')



# ALL API URL PATTERNS
################################################################################
urlpatterns += format_suffix_patterns(router.urls, allowed=ALLOWED_FORMATS)
urlpatterns += format_suffix_patterns(jurisdiction_router.urls, allowed=ALLOWED_FORMATS)





# ADMIN, ADMIN DOC, and PUBLIC DOCS
################################################################################

from django.contrib import admin
from website.views import PublicModelIndexView, PublicModelDetailView

urlpatterns += [
    # Django admin site
    path('admin/',  admin.site.urls),
    # staff-only admin docs
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    # public admin docs, a.k.a. rocdocs
    path(
        'rocdocs/models/',
        PublicModelIndexView.as_view(),
        name='django-admindocs-models-index-public',
    ),
    re_path(
        r'^rocdocs/models/(?P<app_label>[^\.]+)\.(?P<model_name>[^/]+)/$',
        PublicModelDetailView.as_view(),
        name='django-admindocs-models-detail-public',
    ),
]



# DEBUGGING AND PROFILING TOOLS (DEV ONLY)
################################################################################

if settings.DEBUG:
    urlpatterns += [
        path(r'silk/', include('silk.urls', namespace='silk')),
    ]
