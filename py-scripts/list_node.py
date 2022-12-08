from typing import List, Tuple, Any, Dict


class RawListNode:
    _id: int
    _sortorder: int
    _name: str
    _parent: int

    def __init__(self, data: Tuple[Any]):
        self._id = data[0]
        self._name = data[1]
        self._sortorder = data[2]
        self._parent = data[3]

    @property
    def id(self) -> int:
        return self._id
    @property
    def sortorder(self) -> int:
        return self._sortorder

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent(self) -> int:
        return self._parent

    def __str__(self) -> str:
        return f"name: {self._name} (parent: {self._parent} sortorder: {self._sortorder})"

    def __repr__(self) -> str:
        return f"RawListNode(('{self._name}', {self._sortorder}, {self._parent}))"


class ListNode:
    name: str
    children: List['ListNode']

    def __init__(self, rnode: RawListNode):
        self.name = rnode.name

    def add_children(self, childnodes: List['ListNode']) -> None:
        self.children = childnodes

    def printit(self, level: int = 0):
        print(f'{level}: name: {self.name}')
        for x in self.children:
            x.printit(level + 1)