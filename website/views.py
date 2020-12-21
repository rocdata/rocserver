import datetime

from django.contrib.admindocs.views import ModelIndexView, ModelDetailView
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView



def index(request):
    """
    ROC landing page.
    """
    index_context = {}
    return render(request, 'website/index.html', index_context)




# PUBLIC ADMIN DOC FOR MODELS
################################################################################

class PublicModelIndexView(ModelIndexView):
    """
    Autogenerated docs for model list.
    TODO: replace with custom docs page
    """
    template_name = 'admin_doc/model_index_public.html'

    def dispatch(self, request, *args, **kwargs):
        return super(TemplateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['is_nav_sidebar_enabled'] = False
        context_data['site_header'] = 'ROC documentation'
        context_data['site_title'] = 'ROC documentation'
        # import pprint
        # pprint.pprint(context_data)
        return context_data


class PublicModelDetailView(ModelDetailView):
    """
    Autogenerated docs for each model.
    TODO: set order of fields
    """
    template_name = 'admin_doc/model_detail_public.html'

    def dispatch(self, request, *args, **kwargs):
        return super(TemplateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['is_nav_sidebar_enabled'] = False
        # context_data['site_header'] = 'ROC documentation'
        # context_data['site_title'] = 'ROC documentation'
        #import pprint
        # pprint.pprint(context_data)
        return context_data