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
from django.contrib import admin
from django.urls import path, include
#from django.conf.urls import include, url
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from standards.api import JurisdictionViewSet
from standards.api import ControlledVocabularyViewSet
from standards.api import TermViewSet

from standards.api import JurisdictionControlledVocabularyViewSet

router = routers.DefaultRouter()
router.register(r"jurisdiction", JurisdictionViewSet)
router.register(r"vocabulary", ControlledVocabularyViewSet)
router.register(r"term", TermViewSet)  # TODO: change to custom /terms/ APIView

urlpatterns = [
    path('admin/',  admin.site.urls),
    path("api/",    include(router.urls)),
]



jurisdiction_list = JurisdictionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

jurisdiction_detail = JurisdictionViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})
jurisdiction_vocab_detail = JurisdictionControlledVocabularyViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})



urlpatterns += format_suffix_patterns([
    path('terms/', jurisdiction_list, name='jurisdiction-list'),
    path('terms/<name>', jurisdiction_detail, name='jurisdiction-detail'),
    path('terms/<jurisdiction__name>/<name>', jurisdiction_vocab_detail, name='jurisdiction-vocab-detail'),
])
