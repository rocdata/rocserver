import sys

from django.core.management.base import BaseCommand

from standards.models import Jurisdiction
from standards.utils import ensure_country_code, ensure_language_code


class Command(BaseCommand):
    """
    Create a Jurisdiction from attributes specified.
    """
    def add_arguments(self, parser):
        # attributes
        parser.add_argument("--name", required=True, help="the Jurisdiction name used in URIs")
        parser.add_argument("--display_name", help="Official name of the organization or government body")
        parser.add_argument("--country", help="Country of jurisdiction")
        parser.add_argument("--language", help="BCP47 lang codes like en, es, fr-CA")
        parser.add_argument("--notes", help="Public comments and notes about this jurisdiction.")
        #
        # workflow
        parser.add_argument("--overwrite", action='store_true', help="Overwrite existing jurisdiction with same name.")


    def handle(self, *args, **options):

        # try to load jurisdiction if it exists
        try:
            juri = Jurisdiction.objects.get(name=options['name'])
        except Jurisdiction.DoesNotExist:
            juri = None

        if juri and not options['overwrite']:
            print('Jurisdiction', options['name'], 'already exist.')
            print('Use ./manage.py createjurisdiction --overwrite ... to recreate.')
            sys.exit(-8)

        if juri is None:
            juri = Jurisdiction(name=options['name'])

        optional_attrs = ["display_name", "alt_name", "notes", "website_url"]
        for attr in optional_attrs:
            if attr in options and options[attr]:
                setattr(juri, attr, options[attr])

        country_raw = options.get('country', None)
        if country_raw:
            country = ensure_country_code(country_raw)
            juri.country = country
        
        language_raw = options.get('language', None)
        if language_raw:
            language = ensure_language_code(language_raw)
            juri.language = language

        juri.save()
        print('Created jurisdiction', juri.name, '   id=', juri.id)
