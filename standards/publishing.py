from urllib.parse import urlparse
from django.conf import settings



def get_publishing_context(request=None):
    context_name = settings.ROCDATA_PUBLISHING_CONTEXT
    publishing_context = settings.ROCDATA_PUBLISHING_CONTEXTS[context_name]
    if context_name == 'default' and request is None:
        raise ValueError('Default publishing requires request info')
    elif context_name == 'default':
        publishing_context['scheme'] = request.scheme
        publishing_context['netloc'] = request.get_host()
    return publishing_context
