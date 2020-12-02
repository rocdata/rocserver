
URL patterns
============

The Django REST Framework "format suffix patterns" pattern allows us to handle
paths with format extensions like `/terms/Ghana/GradeLevels/B2.json` automatically.

To see this magic, add the following lines to the bottom of `standrads-server/urls.py`:

```python
for urlp in urlpatterns:
    print(urlp)
```

Here is the example debug output:
```python
<URLPattern 'terms/' [name='api-juri-list']>
<URLPattern 'terms<drf_format_suffix_json_html:format>' [name='api-juri-list']>
<URLPattern '^terms/(?P<name>\w*)$' [name='api-juri-detail']>
<URLPattern '^terms/(?P<name>\w*)\.(?P<format>(json|html))/?$' [name='api-juri-detail']>
<URLPattern 'terms/<name>/' [name='api-juri-vocab-list']>
<URLPattern 'terms/<name><drf_format_suffix_json_html:format>' [name='api-juri-vocab-list']>
<URLPattern '^terms/(?P<jurisdiction__name>\w*)/(?P<name>\w*)$' [name='api-juri-vocab-detail']>
<URLPattern '^terms/(?P<jurisdiction__name>\w*)/(?P<name>\w*)\.(?P<format>(json|html))/?$' [name='api-juri-vocab-detail']>
<URLPattern 'terms/<jurisdiction__name>/<name>/' [name='api-juri-vocab-term-list']>
<URLPattern 'terms/<jurisdiction__name>/<name><drf_format_suffix_json_html:format>' [name='api-juri-vocab-term-list']>
<URLPattern '^terms/(?P<vocabulary__jurisdiction__name>\w*)/(?P<vocabulary__name>\w*)/(?P<path>[\w/]*)$' [name='api-juri-vocab-term-detail']>
<URLPattern '^terms/(?P<vocabulary__jurisdiction__name>\w*)/(?P<vocabulary__name>\w*)/(?P<path>[\w/]*)\.(?P<format>(json|html))/?$' [name='api-juri-vocab-term-detail']>
<URLResolver <URLPattern list> (admin:admin) 'admin/'>
```