"""standards-server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns


from website.views import index
from website.views import PublicModelIndexView, PublicModelDetailView



# HIERARCHICAL TERMS API   /api/terms/{juri.name}/{vocab.name}/{term.path}
################################################################################

from standards.api import juri_list, juri_detail
from standards.api import juri_vocab_create, juri_vocab_detail
from standards.api import juri_vocab_term_create, juri_vocab_term_detail

urlpatterns = format_suffix_patterns([
    path('', index, name='index'),
    # Jurisdiction
    # LC
    path('terms/', juri_list, name='api-juri-list'),
    # RUD
    re_path(r'^terms/(?P<name>[\w_\-]*)$', juri_detail, name='api-juri-detail'),
    #
    # Vocabularies (in jurisdiction)
    # C
    path('terms/<name>/', juri_vocab_create, name='api-juri-vocab-list'),
    # RUD
    re_path(r'^terms/(?P<jurisdiction__name>[\w_\-]*)/(?P<name>[\w_\-]*)$', juri_vocab_detail, name='api-juri-vocab-detail'),
    #
    # Terms (in vocab, in jurisdiction)
    # C
    path('terms/<jurisdiction__name>/<name>/', juri_vocab_term_create, name='api-juri-vocab-term-list'),
    # RUD
    re_path(r'^terms/(?P<vocabulary__jurisdiction__name>[\w_\-]*)/(?P<vocabulary__name>[\w_\-]*)/(?P<path>[\w/_\-]*)$',
            juri_vocab_term_detail, name='api-juri-vocab-term-detail'),
], allowed=['json', 'html'])



# FLAT STANDARDS AND CONTENT API
################################################################################

from standards.api import StandardsDocumentViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"documents", StandardsDocumentViewSet, basename='document')

urlpatterns += router.urls






# ADMIN, ADMIN DOC, and PUBLIC DOCS
################################################################################

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





# DEBUG TOOLBAR
################################################################################

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ]
