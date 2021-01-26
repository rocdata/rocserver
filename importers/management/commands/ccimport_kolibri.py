#!/usr/bin/env python
import json
import sys
import os

from django.core.management.base import BaseCommand
import pycountry
import requests

from standards.models import Jurisdiction, Term, jurisdictions
from standards.models import ContentCollection, ContentNode
from standards.utils import ensure_country_code, ensure_language_code



SOURCE_URL_BASE = "https://studio.learningequality.org/en/channels/"


def import_col_from_kolibri_channel(col, kolibri_tree):
    """
    Load the data contained in `kolibri_tree` (JSON) into the collection `col`.
    Nodes that already exist will be updated
    """
    print('in import_col_from_kolibri_channel', col.name, 'titled', col.title)

    # 1. Set content collection attributes from channel attributes
    col.title = kolibri_tree['title']
    col.description = kolibri_tree['description']
    col.language = ensure_language_code(kolibri_tree['lang_id'])  # TODO: add le-utils->pycountries mapping
    col.source_domain = "studio.learningequality.org"
    col.collection_id = kolibri_tree['channel_id']    
    col.source_url = col.source_url if col.source_url else SOURCE_URL_BASE+kolibri_tree['channel_id']
    col.digitization_method = "kolibri_channel"
    col.publication_status = "publicdraft"
    # TODO: parse kolibri_tree['license_name'] || kolibri_tree['license_id']
    col.license = None
    col.license_description = kolibri_tree['license_description']
    col.copyright_holder = kolibri_tree['license_owner']
    # TODO: other nice-to-have attributes:
    #   thumbnail_url
    #   version
    #   published version changelogs? resource counts?  --> extra_fields
    col.save()

    # 2. Add root content node
    add_collection_root_node(col, kolibri_tree)


def add_collection_root_node(col, kolibri_tree):

    try:
        root = col.root
    except ContentNode.DoesNotExist:
        root = ContentNode.objects.create(
            collection=col,
            title='HIDDEN ROOT of ' + col.name,
            description='HIDDEN ROOT of ' + col.name,
        )
    print('root=', root)
    add_children_recursive(root, kolibri_tree['children'])


def add_children_recursive(rocparentnode, children):
    """
    Add the children (list of dicts) to the ROC ContentNode `rocparentnode`.
    """
    print('Adding', len(children), 'children to', rocparentnode.title)
#     for i, child_dict in enumerate(children):        
#         child_node = StandardNode.objects.create(
#             parent=stdnode,
#             document=stdnode.collection,
#             # kind=child_dict["fields"]["kind"]     # TODO
#             sort_order=float(i+1),
#             notation=child_dict["fields"]["identifier"],
#             description=child_dict["fields"]["title"],
#             notes=child_dict["fields"]["notes"],
#             extra_fields=child_dict["fields"]["extra_fields"],
#             source_id=child_dict['pk'],
#         )
#         add_children_recustive(child_node, child_dict['children'])



# NODE
        # {
        #   "author": "",
        #   "available": 1,
        #   "channel_id": "fdab6fb66ba24d05acd011e85bdb36ba",
        #   "children": [
        #     {
        #       "assessment_item_ids": [
        #         "0eef62cf45c65cf9afeca4b6593b7f73",
        #         "46f750a9308f5aaea72f2a062a9919a9",
        #         "85f21d7fc79454e0970aa867e3c2196d",
        #         "960d5673b0b153859fdcd0a4ae7da92f",
        #       ],
        #       "assessmentmetadata": {
        #         "is_manipulable": 1,
        #         "mastery_model": "{\"type\":\"m_of_n\",\"m\":5,\"n\":7}",
        #         "number_of_assessments": 18,
        #         "randomize": 1
        #       },
        #       "author": "",
        #       "available": 1,
        #       "channel_id": "fdab6fb66ba24d05acd011e85bdb36ba",
        #       "coach_content": 0,
        #       "content_id": "ada51f57a22259ac89da5976eb661da8",
        #       "description": "Identify prime numbers less than 100.",
        #       "files": [
        #         {
        #           "available": 1,
        #           "checksum": "9a19b81905f8b1c4aefe162778425039",
        #           "contentnode_id": "99a49cc38358455a9c58e66d1be1d472",
        #           "extension": "perseus",
        #           "file_size": 33969,
        #           "id": "2b3d28a6e02c48c6b105fe7fe33f858c",
        #           "lang_id": null,
        #           "local_file_id": "9a19b81905f8b1c4aefe162778425039",
        #           "preset": "exercise",
        #           "priority": 1,
        #           "supplementary": 0,
        #           "thumbnail": 0
        #         },
        #         {
        #           "available": 1,
        #           "checksum": "89b87f512f3972abdd5c57adbca2fb6d",
        #           "contentnode_id": "99a49cc38358455a9c58e66d1be1d472",
        #           "extension": "png",
        #           "file_size": 21949,
        #           "id": "c11ca383f7a54455a280ca6f47bcd7b0",
        #           "lang_id": null,
        #           "local_file_id": "89b87f512f3972abdd5c57adbca2fb6d",
        #           "preset": "exercise_thumbnail",
        #           "priority": 2,
        #           "supplementary": 1,
        #           "thumbnail": 1
        #         }
        #       ],
        #       "id": "99a49cc38358455a9c58e66d1be1d472",
        #       "kind": "exercise",
        #       "lang_id": "en",
        #       "level": 3,
        #       "lft": 4,
        #       "license_description": "Permission granted to distribute through Kolibri for non-commercial use",
        #       "license_id": 2,
        #       "license_name": "Special Permissions",
        #       "license_owner": "Khan Academy",
        #       "parent_id": "355a543c327640d19f0c9b100aada80c",
        #       "rght": 5,
        #       "sort_order": 5.0,
        #       "stemmed_metaphone": "ATNTF PRM NMPR ATNTF PRM NMPR LS 0N TN",
        #       "title": "Identify prime numbers",
        #       "tree_id": 1
        #     },


class Command(BaseCommand):
    """
    Import a kolibri tree JSON dump obtained from a Kolibri content channel DB.
    """
    def add_arguments(self, parser):
        parser.add_argument("path", help="A local path or URL for the collection to import")
        # attributes
        parser.add_argument("--jurisdiction", required=True, help="Jurisdiction name")
        parser.add_argument("--name", required=True, help="short name for content collection")
        parser.add_argument("--country", help="Country where content collection was produced")
        parser.add_argument("--source_domain", help="Collection source domain")
        parser.add_argument("--source_url", help="Collection source URL")
        parser.add_argument("--kolibritree_url", help="Location of ")
        # parser.add_argument("--language", help="BCP47 lang codes like en, es, fr-CA")
        # workflow
        parser.add_argument("--update", action='store_true', help="Update an existing collection with new data.")


    def handle(self, *args, **options):
        # Parse and validate Jurisdiction
        jurisdiction_name = options['jurisdiction']
        try:
            juri = Jurisdiction.objects.get(name=jurisdiction_name)
        except Jurisdiction.DoesNotExist:
            print('Jurisdiction', jurisdiction_name, 'does not exist yet')
            print('Use the ./manage.py createjurisdiction command to create it')
            sys.exit(-5)

        # Load kolibri channel JSON data
        path = options['path']
        print('Loading content collection from path', path)
        if path.startswith('http'):
            response = requests.get(path)
            json_text = response.text
        else:
            json_text = open(path).read()
        kolibri_tree = json.loads(json_text)

        # Check if already exists or create
        colname = options['name']
        try:
            col = ContentCollection.objects.get(jurisdiction=juri, name=colname)
            updating_existing = True
        except ContentCollection.DoesNotExist:
            col = None
            updating_existing = False
        if col and not options['update']:
            print('Content collection', options['name'], 'already exist.')
            print('Use ./manage.py ccimport_kolibri --update to re-create.')
            # TODO: 
            sys.exit(-8)
        if col is None:
            col = ContentCollection(jurisdiction=juri, name=colname)

        # Set collection attributes
        optional_attrs = ["source_domain", "source_url"]
        for attr in optional_attrs:
            if attr in options and options[attr]:
                setattr(juri, attr, options[attr])
        country_raw = options.get('country', None)
        if country_raw:
            country = ensure_country_code(country_raw)
            juri.country = country
        
        # Save it
        col.save()

        # Add nodes
        import_col_from_kolibri_channel(col, kolibri_tree)
        if updating_existing:
            print('Updated content collection', col.name, '   id=', col.id)
        else:
            print('Created content collection', col.name, '   id=', col.id)

