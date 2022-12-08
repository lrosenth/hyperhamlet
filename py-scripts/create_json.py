import json
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
    "project": {
        "shortcode": "0841",
        "shortname": "hyperhamlet",
        "longname": "Hyperhamlet",
        "descriptions": {
            "en": "Hyperhamlet"
        },
        "keywords": {
            "Shakespeare", "cultural history"
        },
        "lists": []
    }
}


def get_list(con: mariadb.Connection, name: str) -> List[RawListNode]:
    cursor = con.cursor()
    cursor.execute(f"SELECT * FROM {name}")
    res = cursor.fetchone()
    nodes: List[RawListNode] = []
    while res:
        nodes.append(RawListNode(res))
        res = cursor.fetchone()
    cursor.close()
    return nodes


def process_list(nodes: List[RawListNode]):
    toprawnodes = [x for x in nodes if x.parent is None]
    toprawnodes.sort(key=lambda node: node.sortorder)
    topnodes = [ListNode(x) for x in toprawnodes]


def to_node_with_children(rawnode: RawListNode, rawnodes: List[RawListNode]):
    children: List[ListNode] = []
    rawchildren = [x for x in rawnodes if x is not None and x.parent == rawnode.id]
    rawchildren.sort(key=lambda x: x.sortorder)
    for x in rawchildren:
        children.append(to_node_with_children(x, rawnodes))
    node = ListNode(rawnode)
    node.add_children(children)
    return node



con = mariadb.connect(**mariadb_params)

rawnodes = get_list(con, "quotmarks")
toprawnodes = [x for x in rawnodes if x.parent is None]
toprawnodes.sort(key=lambda node: node.sortorder)

topnodes = [to_node_with_children(x, rawnodes) for x in toprawnodes]
for y in topnodes:
    y.printit()


con.close()
