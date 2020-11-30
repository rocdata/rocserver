
import os
import sys

from django.core.management.base import BaseCommand
import pycountry
import requests
import yaml

from standards.models import Jurisdiction, ControlledVocabulary, Term, TermRelation




def ensure_language_code(lang_code):
    """
    Pass-through function for alpha_2 langauge codes that ensures validity.
    """
    lang_obj = pycountry.languages.get(alpha_2=lang_code)
    if lang_obj is None:
        print('ERROR: invalid language code specified', lang_code)
        sys.exit(-4)
    return lang_obj.alpha_2



class Command(BaseCommand):
    """
    Import a controlled vocabulary from YAML data (local or from a repo link).
    """

    def load_terms_data(self, termsdata, options):
        """
        Process the `termsdata` (dict) to create ControlledVocabulary and Terms.
        """
        assert termsdata['type'] == 'ControlledVocabulary'
        # 
        vocab_language = ensure_language_code(termsdata.get('language', 'en'))
        #
        country_raw = termsdata.get('country', None)
        if country_raw:
            country = pycountry.countries.lookup(country_raw).alpha_2
        else:
            country = None
        #
        jurisdiction_name = termsdata['jurisdiction']
        if 'jurisdiction' in options and options['jurisdiction']:
            jurisdiction_name = options['jurisdiction']
        try:
            juri = Jurisdiction.objects.get(name=jurisdiction_name)
        except Jurisdiction.DoesNotExist:
            print('Jurisdiction', jurisdiction_name, 'does not exist yet')
            print('Use the ./manage.py createjurisdiction command')
            sys.exit(-5)

        vocab_name = termsdata['name'].strip()
        vocab = ControlledVocabulary.objects.get(name=vocab_name, jurisdiction=juri)
        if vocab and not options['overwrite']:
            print('Vocabulary', vocab, 'already exist. Use --overwrite to overwrite.')
            sys.exit(-6)
        if vocab and options['overwrite']:
            vocab.label = termsdata.get('label') or termsdata['title']
            vocab.description = termsdata.get('description')
            vocab.source = termsdata.get('source')
            vocab.country = country
            vocab.save()
            print('Vocab', vocab, 'already exists; overwriting terms.')
            Term.objects.filter(vocabulary=vocab).delete()
        else:
            vocab = ControlledVocabulary(
                name=vocab_name,                       # TODO: check if URL-safe
                label=termsdata.get('label') or termsdata['title'],
                description=termsdata.get('description'),
                language=vocab_language,
                source=termsdata.get('source'),
                country=country,
                jurisdiction=juri,
            )
            vocab.save()
            print('Created vocab:', vocab)

        print('Adding', len(termsdata['terms']), 'terms to vocab...')
        for idx, term_dict in enumerate(termsdata['terms']):
            term_path = term_dict['term'].strip()
            label = term_dict.get('label') or name.title()
            term_language_raw = termsdata.get('language', None)
            if term_language_raw:
                term_language = ensure_language_code(term_language_raw)
            else:
                term_language = vocab_language
            term = Term(
                path=term_path,                        # TODO: check if URL-safe
                label=label,
                vocabulary=vocab,
                sort_order=float(idx+1),
                language=term_language,
            )
            OPTIONAL_ATTRS = ['definition', 'notes', 'alt_label', 'hidden_label']
            for attr in OPTIONAL_ATTRS:
                val = term_dict.get(attr)
                if val:
                    setattr(term, attr, val)
            term.save()

        print('DONE')

        # TODO: check termsdata.get('uri') maches vocab.uri



    def add_arguments(self, parser):
        parser.add_argument(
            "--jurisdiction", help="The Jurisdiction name for this vocabulary."
        )
        parser.add_argument(
            "--overwrite", action='store_true', help="Overwrite existing vocabulary with same name."
        )
        parser.add_argument(
            "path", help="A local path or URL path for the vocabulary to import."
        )
        # parser.add_argument(
        #     "--status", type=bool, default=True, help="Set to false when ready."
        # )


    def handle(self, *args, **options):
        """
        Import the controleld vocabulary and the terms defined in the file `path`.
        """
        path = options['path']
        print('Loading controlled vocabulary and terms data from', path)
        print(os.getcwd())
        
        if path.startswith('http'):
            response = requests.get(path)
            yaml_text = response.text
        else:
            full_path = os.path.join('.', path)
            print(full_path)
            yaml_text = open(path).read()

        termsdata = yaml.safe_load(yaml_text)
        if termsdata is None:
            print('ERROR: no data can available at', path)
            sys.exit(-3)

        self.load_terms_data(termsdata, options)
