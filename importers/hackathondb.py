#!/usr/bin/env python
import sys, os, django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "standards-server.settings")
django.setup()

from standards.models import UserProfile
from standards.models import Jurisdiction, ControlledVocabulary, Term, TermRelation
from standards.models import StandardNode, StandardsDocument


if __name__ == '__main__':
    for juri in Jurisdiction.objects.all():
        print(juri.name)
        for vocab in ControlledVocabulary.objects.filter(jurisdiction=juri):
            print(' -', vocab.name, 'containing', len(vocab.terms.all()), 'terms')
        print('---')