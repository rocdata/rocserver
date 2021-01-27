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


# Studio Source URL templates
STUDIO_SOURCE_URL_BASE_TMPL = "https://studio.learningequality.org/en/channels/{channel_id}"
STUDIO_FILE_URL_BASE = "https://studio.learningequality.org/content/storage/"

# Kolibri demoserver instance URL templates
KOLIBRI_CHANNEL_SOURCE_URL_TMPL = "{demoserver}/en/learn/#/topics/{channel_id}"
# e.g. http://alejandro-demo.learningequality.org/en/learn/#/topics/fdab6fb66ba24d05acd011e85bdb36ba
KOLIBRI_TOPIC_SOURCE_URL_TMPL = "{demoserver}/en/learn/#/topics/t/{node_id}"
# e.g. http://alejandro-demo.learningequality.org/en/learn/#/topics/t/501bff553f464e7f8a27ff3bef689d40
KOLIBRI_CONTENTNODE_SOURCE_URL_TMPL = "{demoserver}/en/learn/#/topics/c/{node_id}"
# e.g. http://alejandro-demo.learningequality.org/en/learn/#/topics/c/a1602eb28a014abb9d5e724eaed42e23


def import_col_from_kolibri_channel(col, kolibri_tree, options):
    """
    Load the data contained in `kolibri_tree` (JSON) into the collection `col`.
    Nodes that already exist will be updated
    """
    print('in import_col_from_kolibri_channel', col.name, 'titled', col.title)

    # 1. Set content collection attributes from channel attributes
    col.title = kolibri_tree['title']
    col.description = kolibri_tree['description']
    if col.source_domain is None:
        col.source_domain = "studio.learningequality.org"
    col.collection_id = kolibri_tree['channel_id']
    col.digitization_method = "kolibri_channel"
    col.publication_status = "publicdraft"
    # TODO: parse kolibri_tree['license_name'] || kolibri_tree['license_id']
    col.license = None
    col.license_description = kolibri_tree['license_description']
    col.copyright_holder = kolibri_tree['license_owner']

    # Set collection language (prefer collection language specified on command line)
    if 'language' in options and options['language']:
        col.language = ensure_language_code(options['language'])
    else:
        channel_language = kolibri_tree['lang_id']
        # TODO: add le-utils -> pycountries mapping
        col.language = ensure_language_code(channel_language)

    # Set source_url
    # Use demoserver or source_url if specified, else fallback to studio URL
    if 'demoserver' in options and options['demoserver']:
        demoserver = options['demoserver']
        col.source_url = KOLIBRI_CHANNEL_SOURCE_URL_TMPL.format(
                demoserver=demoserver,
                channel_id=kolibri_tree['channel_id'])
    elif col.source_url:
        col.source_url =  col.source_url
    else:
        col.source_url = STUDIO_SOURCE_URL_BASE_TMPL.format(channel_id=kolibri_tree['channel_id'])
    # version TODO
    # Other nice-to-have attributes:
    #   thumbnail_url
    #   published version changelogs? resource counts? -> extra_fields
    col.save()

    # 2. Add root content node
    root = add_collection_root_node(col, kolibri_tree)

    # 3. Recursively add children
    add_children_recursive(root, kolibri_tree['children'], options)



def add_collection_root_node(col, kolibri_tree):
    """
    Get or create the collection root node. Note this is a logically "hidden"
    node that should not be visible to end users of the ROC server.
    """
    try:
        root = col.root
    except ContentNode.DoesNotExist:
        root = ContentNode.objects.create(
            collection=col,
            title='HIDDEN ROOT of ' + col.name,
            description='HIDDEN ROOT of ' + col.name,
            language=col.language,     # used for inherit-lang-from-parent logic
        )
    return root


KOLIBRI_KIND_TO_ContentNodeKind_MAP = {}
kind_terms = Term.objects.filter(
    vocabulary__jurisdiction__name="LE",
    vocabulary__name="KolibriContentNodeKinds")
for kind_term in kind_terms:
    KOLIBRI_KIND_TO_ContentNodeKind_MAP[kind_term.path] = kind_term

KOLIBRI_LICENSE_NAME_TO_LicenseKind_MAP = {}
license_terms = Term.objects.filter(
    vocabulary__jurisdiction__name="LE",
    vocabulary__name="LicenseKinds")
for license_term in license_terms:
    KOLIBRI_LICENSE_NAME_TO_LicenseKind_MAP[license_term.label] = license_term


def add_children_recursive(rocparentnode, children, options):
    """
    Add `children` (list of Kolibri node dicts) to `rocparentnode` (ContentNode).
    """
    print('  - Adding', len(children), 'children to', rocparentnode.title)

    oldchildren = rocparentnode.children.all()
    oldchildren_by_source_id = dict((och.source_id, och) for och in oldchildren)
    oldchildren.delete()

    for i, child_dict in enumerate(children):

        child_node = ContentNode.objects.create(
            # Structural
            collection=rocparentnode.collection,
            parent=rocparentnode,
            kind=KOLIBRI_KIND_TO_ContentNodeKind_MAP[child_dict["kind"]],
            sort_order=float(i+1),
            # Content info
            title=child_dict["title"],
            description=child_dict["description"],
            language = ensure_language_code(child_dict.get('lang_id', rocparentnode.language)),
            author=child_dict["author"],
            # aggregator and provider not available from Kolibri DB; only Studio
            # Content source info
            source_id=child_dict['id'],  # Kolibri node_id (unique within channel)
            content_id=child_dict['content_id'],
            node_id=child_dict['id'],
            # Licensing
            license = KOLIBRI_LICENSE_NAME_TO_LicenseKind_MAP.get(child_dict.get("license_name")),
            license_description=child_dict.get('license_description'),
            copyright_holder=child_dict.get('license_owner'),
        )
        # OTHER (FUTURE):
        #   path?
        #   source_domain => not accessible from Kolibri DB, but this info would
        #                    be good to have for source_domain:source_id ids.
        #   subjects/education_levels/concept_terms/concept_keywords/tags FUTURE

        if 'demoserver' in options and options['demoserver']:
            demoserver = options['demoserver']
            kind = child_dict["kind"]
            if kind == 'topic':
                source_url = KOLIBRI_TOPIC_SOURCE_URL_TMPL.format(
                    demoserver=demoserver,
                    node_id=child_dict['id'])
            else:
                source_url = KOLIBRI_CONTENTNODE_SOURCE_URL_TMPL.format(
                    demoserver=demoserver,
                    node_id=child_dict['id'])
            child_node.source_url = source_url

        # Process files and assessment items associated with this content node
        total_file_size = 0        # Total file storage size required (in bytes)
        node_extra_fields = {}     # Store info about files and assessment items
        if 'files' in child_dict:
            file_extra_list = []
            for file_dict in child_dict['files']:
                md5 = file_dict["checksum"]
                file_extra = dict(
                    checksum=file_dict["checksum"],
                    extension=file_dict["extension"],
                    file_size=file_dict["file_size"],
                    lang_id=file_dict["lang_id"],
                    preset=file_dict["preset"],
                    file_url=STUDIO_FILE_URL_BASE + md5[0] + '/' + md5[1] + '/' + md5 + '.' + file_dict["extension"],
                )
                file_extra_list.append(file_extra)
                total_file_size += file_dict['file_size']
            node_extra_fields['files'] = file_extra_list
        if 'assessmentmetadata' in child_dict:
            node_extra_fields['assessmentmetadata'] = {}
            node_extra_fields["assessmentmetadata"]["number_of_assessments"] = \
                   child_dict["assessmentmetadata"]["number_of_assessments"]

        child_node.size = total_file_size
        child_node.extra_fields = node_extra_fields


        child_node.save()

        # Recurse into children
        if 'children' in child_dict:
            add_children_recursive(child_node, child_dict['children'], options)


class Command(BaseCommand):
    """
    Import a kolibri tree JSON dump obtained from a Kolibri content channel DB.
    """
    def add_arguments(self, parser):
        parser.add_argument("path", help="A local path or URL for the collection data (JSON kolibri tree)")
        # attributes
        parser.add_argument("--jurisdiction", required=True, help="Jurisdiction name")
        parser.add_argument("--name", required=True, help="short name for content collection")
        parser.add_argument("--country", help="Country where content collection was produced")
        parser.add_argument("--language", help="BCP47 lang codes like en, es, fr-CA")
        parser.add_argument("--source_domain", help="Collection source domain")
        parser.add_argument("--source_url", help="Collection source URL")
        parser.add_argument("--demoserver", help="Link to a Kolibri instance to use for source_url links")
        parser.add_argument("--notes", help="Additional info about this collection")
        #
        # workflow
        parser.add_argument("--update", action='store_true', help="Update an existing collection with new data.")


    def handle(self, *args, **options):
        # options cleaning
        if 'demoserver' in options and options['demoserver'] and options['demoserver'].endswith('/'):
            options['demoserver'] = options['demoserver'].rstrip('/')

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
        optional_attrs = ["source_domain", "notes"]
        for attr in optional_attrs:
            if attr in options and options[attr]:
                setattr(col, attr, options[attr])

        country_raw = options.get('country', None)
        if country_raw:
            country = ensure_country_code(country_raw)
            col.country = country

        language_raw = options.get('language', None)
        if language_raw:
            language = ensure_language_code(language_raw)
            col.language = language

        # Save it
        col.save()

        # Add nodes
        import_col_from_kolibri_channel(col, kolibri_tree, options)
        if updating_existing:
            print('Updated content collection', col.name, '   id=', col.id)
        else:
            print('Created content collection', col.name, '   id=', col.id)
