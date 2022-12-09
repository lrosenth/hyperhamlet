import json
from pprint import pprint
from typing import List

from list_node import RawListNode, ListNode

import mariadb

mariadb_params = {
    "user": "root",
    "password": "rgs455",
    "host": "localhost",
    "database": "hyperhamlet"
}

datamodel = {
    "$schema": "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/ontology.json",
    "project": {
        "shortcode": "0841",
        "shortname": "hyperhamlet",
        "longname": "Hyperhamlet",
        "descriptions": {
            "en": "Hyperhamlet"
        },
        "keywords": [
            "Shakespeare",
            "cultural history"
        ],
        "lists": [
            {
                "name": "linetypes",
                "labels": {"en": "Linetypes"},
                "nodes": [
                    {
                        "name": "Text",
                        "labels": {"en": "Text"}
                    },
                    {
                        "name": "heading",
                        "labels": {"en": "Heading"}
                    },
                    {
                        "name": "stage",
                        "labels": {"en": "Stage"}
                    },
                    {
                        "name": "speaker",
                        "labels": "Speaker"
                    }
                ]
            }
        ],
        "ontologies": [{
            "name": "Hyperhamlet",
            "description": "Hyperhamlet ontology",
            "properties": [
                {
                    "name": "hasLineId",
                    "super": ["hasValue"],
                    "object": "IntValue",
                    "labels": {"en": "ID"},
                    "gui_element": "SimpleText",
                    "gui_attributes": {
                        "maxlength=": 5,
                        "size": 6
                    }
                },
                {
                    "name": "hasLineNumber",
                    "super": ["hasValue"],
                    "object": "IntValue",
                    "labels": {"en": "Line number"},
                    "gui_element": "SimpleText",
                    "gui_attributes": {
                        "maxlength=": 5,
                        "size": 6
                    }
                },
                {
                    "name": "hasLinetext",
                    "super": ["hasValue"],
                    "object": "TextValue",
                    "labels": {"en": "Linetext"},
                    "gui_element": "SimpleText",
                    "gui_attributes": {
                        "maxlength=": 255,
                        "size": 80
                    }
                },
                {
                    "name": "inAct",
                    "super": ["hasValue"],
                    "object": "IntValue",
                    "labels": {"en": "Act"},
                    "gui_element": "Spinbox",
                    "gui_attributes": {
                        "max": 5.0,
                        "min": 1.0
                    }
                },
                {
                    "name": "inScene",
                    "super": ["hasValue"],
                    "object": "IntValue",
                    "labels": {"en": "Scene"},
                    "gui_element": "Spinbox",
                    "gui_attributes": {
                        "max": 7.0,
                        "min": 1.0
                    }
                },
                {
                    "name": "hasLineType",
                    "super": ["hasValue"],
                    "object": "ListValue",
                    "labels": {"en": "Linetype"},
                    "gui_element": "List",
                    "gui_attributes": {
                        "hlist": "linetypes"
                    }
                }
            ],
            "resources": [
                {
                    "name": "hamlettext",
                    "labels": {
                        "en": "hamlettext"
                    },
                    "super": "Resource",
                    "cardinality": [
                        {
                            "propname": "hasLineId",
                            "gui_order": 1,
                            "cardinality": "1"
                        },
                        {
                            "propname": "hasLineNumber",
                            "gui_order": 2,
                            "cardinality": "1"
                        },
                        {
                            "propname": "hasLinetext",
                            "gui_order": 3,
                            "cardinality": "1"
                        },
                        {
                            "propname": "hasLineType",
                            "gui_order": 4,
                            "cardinality": "1"
                        },
                        {
                            "propname": "inAct",
                            "gui_order": 5,
                            "cardinality": "1"
                        },
                        {
                            "propname": "inScene",
                            "gui_order": 6,
                            "cardinality": "1"
                        },
                    ]
                }
            ]
        }]
    }
}


def get_list(con: mariadb.Connection, name: str) -> List[ListNode]:
    cursor = con.cursor()
    cursor.execute(f"SELECT * FROM {name}")
    res = cursor.fetchone()
    rawnodes: List[RawListNode] = []
    while res:
        rawnodes.append(RawListNode(res))
        res = cursor.fetchone()
    cursor.close()

    toprawnodes = [x for x in rawnodes if x.parent is None]
    toprawnodes.sort(key=lambda node: node.sortorder)

    topnodes = [to_node_with_children(x, rawnodes) for x in toprawnodes]

    return topnodes



def to_node_with_children(rawnode: RawListNode, rawnodes: List[RawListNode]):
    children: List[ListNode] = []
    rawchildren = [x for x in rawnodes if x is not None and x.parent == rawnode.id]
    rawchildren.sort(key=lambda x: x.sortorder)
    for x in rawchildren:
        children.append(to_node_with_children(x, rawnodes))
    node = ListNode(rawnode)
    node.add_children(children)
    return node


def nodes_to_dict(name: str, comment: str, nodes: List[ListNode]):

    def process_one_node(node: ListNode):
        tmpobj = {
            "name": node.name,
            "labels": {
                "en": node.name
            }
        }
        if node.children:
            tmpobj["nodes"] = []
            for child in node.children:
                tmpobj["nodes"].append(process_one_node(child))
        return tmpobj

    listdict = {
        "name": name,
        "labels": {
            "en": name
        },
        "comments": {
            "en": comment
        },
    }
    if nodes:
        listdict["nodes"] = []
        for node in nodes:
            listdict["nodes"].append(process_one_node(node))
    return listdict

con = mariadb.connect(**mariadb_params)

listnames = [
    "authormarks",
    "generals",
    "intertextuals",
    "languages",
    "linecategories"
]

for listname in listnames:
    topnodes = get_list(con, listname)
    listdict = nodes_to_dict(listname, "a comment", topnodes)
    datamodel["project"]["lists"].append(listdict)

jsonstr = json.dumps(datamodel, indent=3)
with open("hyperhamlet.json", "w") as outfile:
    outfile.write(jsonstr)

con.close()
