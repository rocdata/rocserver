#!/usr/bin/env python
import json
import yaml
import sys
import os
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "standards-server.settings")
django.setup()

from standards.models import UserProfile
from standards.models import Jurisdiction, ControlledVocabulary, Term, TermRelation
from standards.models import StandardNode, StandardsDocument


DUMPADTAS_DIR = os.path.join(BASE_DIR, "..", "standards-hackathon", "dumpdatas")
DOCS_DUMPDATA_FILENAME = "hackathon_CurriculumDocument_data.json"
NODES_DUMPDATA_FILENAME = "hackathon_StandardNode_data.json"
JUDGMENTS_DUMPDATA_FILENAME = "hackathon_HumanRelevanceJudgment_data.json"

JURISDICTION_SOURCE_IDS = {
    "CCSS": [],
    "NGSS": [],
}


DOCS_TO_IMPORT_BY_SOURCE_ID = {
    "CCSSM": {
        "source_id": "CCSSM",
        "jurisdiction": "USA",
        "name": "CCSS.Math",
        "title": "Common Core State Standards for Mathematics",
        "language": "en",
        "country": "US",
        "publisher": "NGA Center for Best Practices and the Council of Chief State School Officers",
        "license_description": "© Copyright 2010. National Governors Association Center for Best Practices and Council of Chief State School Officers. All rights reserved.",    
        "digitization_method": "hackathon_import",
        "source_doc": "http://www.corestandards.org/Math/",
    },
}
#     {   "source_id": australia_standards_australia_science_f-10
#     {   "source_id": australia_standards_australia_mathematics_f-10
#     {   "source_id": australia_standards_technologies_f-10
#     {   "source_id": australia_standards_australia_work_studies_f-10
#     {   "source_id": CA-CTE
#     {   "source_id": zambia-math-5to7
#     {   "source_id": zambia-english-5to7
#     {   "source_id": gov.uk.math
#     {   "source_id": gov.uk.science
#     {   "source_id": kicd-secondary-vol-ii


# SKIPPED
# khan_academy_us
# kenya-math
# KICDvolumeII



def pathstr_to_pathlist(pathstr):
    depth = len(pathstr)/4
    pathlist = []
    for startpos in range(0, len(pathstr), 4):
        pathlist.append(pathstr[startpos:startpos+4])
    assert len(pathlist) == depth
    return pathlist


def annotate_nodes(doc_nodes):
    for nd in doc_nodes:
        pathlist = pathstr_to_pathlist(nd['fields']["path"])
        nd['pathlist'] = pathlist
        nd['parent'] = pathlist[0:-1]
    return doc_nodes


def get_children(parent, doc_nodes):
    children = []
    for nd in doc_nodes:
        if nd["parent"] == parent['pathlist']:
            children.append(nd)
    sorted_children = sorted(children, key=lambda nd: nd["fields"]["sort_order"])
    return sorted_children


def import_doc(doc_dict):
    doc = doc_dict["fields"]
    source_id = doc["source_id"]
    doc_pk = doc_dict["pk"]
    print('in import_doc', doc["source_id"], 'titled', doc["title"])

    # 1. Document
    juri = Jurisdiction.objects.get(name="CCSS")
    doc_info = DOCS_TO_IMPORT_BY_SOURCE_ID[source_id]
    print(doc_info)

    try:
        stddoc = StandardsDocument.objects.get(name=doc_info["name"], jurisdiction=juri)
        print("Deleting old verison of curriculum document...")
        stddoc.delete()
    except StandardsDocument.DoesNotExist:
        pass

    stddoc = StandardsDocument.objects.create(name=doc_info["name"], jurisdiction=juri)
    stddoc.title=doc_info['title']
    stddoc.language=doc_info['language']
    stddoc.country=doc_info['country']
    stddoc.publisher=doc_info['publisher']
    stddoc.license_description=doc_info['license_description']
    stddoc.digitization_method=doc_info['digitization_method']
    stddoc.source_doc=doc_info['source_doc']
    stddoc.source_id=doc_dict['pk']
    stddoc.save()
    print('created...')
    print(stddoc)

    # 2. Nodes
    doc_nodes_cache_yaml = 'doc_nodes_' + str(doc_pk) + '.yml'
    if os.path.exists(doc_nodes_cache_yaml):
        print("loading form cache...")
        doc_nodes = yaml.safe_load(open(doc_nodes_cache_yaml).read())
    else:
        print('selecting inneficiently from list; this may take some time...')
        nodes_path = os.path.join(DUMPADTAS_DIR, NODES_DUMPDATA_FILENAME)
        allnodes_list = yaml.safe_load(open(nodes_path).read())
        doc_nodes = [nd for nd in allnodes_list if nd['fields']['document'] == doc_pk]
        with open(doc_nodes_cache_yaml, 'w') as cachef:
            cachef.write(yaml.dump(doc_nodes, sort_keys=False))

    print("Found", len(doc_nodes), 'nodes for this document')
    doc_nodes = annotate_nodes(doc_nodes)

    dict_tree = treeify_doc_dict(doc_dict, doc_nodes)

    root = StandardNode.objects.create(
        document=stddoc,
        description='ROOT',
        sort_order=1.0,
    )
    print('root=', root)
    add_children_recustive(root, dict_tree['children'])

    


# Dicts processing
################################################################################

def add_children(node_dict, doc_nodes):
    children = get_children(node_dict, doc_nodes)
    node_dict['children'] = []
    for child in children:
        node_dict['children'].append(child)
        add_children(child, doc_nodes)

def treeify_doc_dict(doc_dict, doc_nodes):
    roots = [nd for nd in doc_nodes if nd["parent"] == []]
    assert len(roots) == 1
    root = roots[0]
    add_children(root, doc_nodes)

    doc_dict['children'] = root['children']
    
    with open('tmptree.json', 'w') as jsonf:
        json.dump(doc_dict, jsonf, indent=2, ensure_ascii=False, sort_keys=False)

    return doc_dict



# Django models
################################################################################

def add_children_recustive(stdnode, children):
    # print('processing', len(children))
    for i, child_dict in enumerate(children):        
        child_node = StandardNode.objects.create(
            parent=stdnode,
            document=stdnode.document,
            # kind=child_dict["fields"]["kind"]     # TODO
            sort_order=float(i+1),
            notation=child_dict["fields"]["identifier"],
            description=child_dict["fields"]["title"],
            notes=child_dict["fields"]["notes"],
            extra_fields=child_dict["fields"]["extra_fields"],
            source_id=child_dict['pk'],
        )
        add_children_recustive(child_node, child_dict['children'])



# CLI
################################################################################

if __name__ == '__main__':
    # Load documents
    docs_path = os.path.join(DUMPADTAS_DIR, DOCS_DUMPDATA_FILENAME)
    docs_list = yaml.safe_load(open(docs_path).read())
    if docs_list is None:
        print('ERROR: no data can available at', path)
        sys.exit(-3)
    
    source_ids_to_import = DOCS_TO_IMPORT_BY_SOURCE_ID.keys()
    for doc_dict in docs_list:
        doc = doc_dict["fields"]
        source_id = doc["source_id"]
        if source_id in source_ids_to_import:
            print('Importing doc  source_id=' , doc["source_id"], 'titled', doc["title"])
            import_doc(doc_dict)

    print('DONE')
