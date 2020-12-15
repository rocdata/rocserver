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
from rest_framework.urlpatterns import format_suffix_patterns

from standards.api import JurisdictionViewSet, JurisdictionVocabularyViewSet, JurisdictionVocabularyTermViewSet


# HEARARCHICAL API   /api/terms/{juri_name}/{vocab_name}/{term_path}
################################################################################

juri_list = JurisdictionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
juri_detail = JurisdictionViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

juri_vocab_list = JurisdictionVocabularyViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
juri_vocab_detail = JurisdictionVocabularyViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

juri_vocab_term_list = JurisdictionVocabularyTermViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
juri_vocab_term_detail = JurisdictionVocabularyTermViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = format_suffix_patterns([
    #
    # jurisdiction CRUD
    path('terms/', juri_list, name='api-juri-list'),
    re_path(r'^terms/(?P<name>[\w_\-]*)$',
            juri_detail, name='api-juri-detail'),
    #
    # vocab CRUD  (in jurisdiction)
    path('terms/<name>/', juri_vocab_list, name='api-juri-vocab-list'),  # -> juri_vocab_create
    re_path(r'^terms/(?P<jurisdiction__name>[\w_\-]*)/(?P<name>[\w_\-]*)$',
            juri_vocab_detail, name='api-juri-vocab-detail'),
    path('terms/<jurisdiction__name>/<name>/', juri_vocab_term_list, name='api-juri-vocab-term-list'), # -> juri_vocab_term_create
    #
    # term CRUD (in vocab, in jurisdiction)
    re_path(r'^terms/(?P<vocabulary__jurisdiction__name>[\w_\-]*)/(?P<vocabulary__name>[\w_\-]*)/(?P<path>[\w/_\-]*)$',
            juri_vocab_term_detail, name='api-juri-vocab-term-detail'),
], allowed=['json', 'html'])


urlpatterns += [
    path('admin/',  admin.site.urls),
]



if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ]
