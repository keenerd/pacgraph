#! /usr/bin/env python

from itertools import *

# 629 nodes: 90.28 -> 83.62 -> 53.78 -> 44.73
# 3526 nodes: 2897.06 -> 2664.81 -> 1470.74

def common_ranges(r1, r2):
    "returns true if overlap"
    if r1[0] < r2[0]:  # list/tuple comp
        return r1[1] > r2[0]
    return r2[1] > r1[0]

def in_box(bbox1, bbox2):
    cr = common_ranges
    r1x = bbox1[0::2]
    r1y = bbox1[1::2]
    r2x = bbox2[0::2]
    r2y = bbox2[1::2]
    return cr(r1y, r2y) and cr(r1x, r2x)




class Rtree(object):
    "Why?  Pyrtree is insert-then-query (but mine has no delete), Rtree has crazy C deps."
    def __init__(self, parent=None, box=None, name=None):
        "Only root has no parent, only leaves have names."
        # Half an R-tree.  Not height balanced!  Missing delete().
        bigm = 5
        self.parent = parent
        self.name = name
        self.bigm = bigm
        self.lilm = bigm//2
        self.children = []
        self.box = (0,0,0,0)
        if box:
            self.box = tuple(box)
    def show(self, depth=0):
        head = '  ' * depth + str(self.box) + ' '
        if self.name:
            return head + self.name + '\n'
        head += str(len(self.children))
        return head + '\n' + ''.join(c.show(depth+1) for c in self.children)
    def root(self):
        if self.parent is None:
            return self
        return self.parent.root()
    def best_node(self, to_add):
        "smallest place for box to_add, does not change anything"
        return smallest_merge(self.children, to_add)
    def search(self, box=None):
        "yields matching leaf objects, no box for all leaves"
        todo = [self]
        while todo:
            node = todo.pop()
            if box and not in_box(node.box, box):
                continue
            if node.name:
                yield node
            todo.extend(node.children)
    def insert(self, box, name=None):
        "makes a new node"
        target = self.root().choose_leaf(box)
        target.children.append(Rtree(target, box, name))
        target.merge_up(box)
        if len(target.children) > target.bigm:
            target.divide_children()
    def merge_up(self, box):
        # only grows
        new_box = merge(self.box, box)
        if new_box == self.box:
            return
        self.box = new_box
        if self.parent:
            self.parent.merge_up(self.box)
    def is_leaf_node(self):
        return (not self.children) or bool(self.children[0].name)
    def choose_leaf(self, box):
        n = self
        while not n.is_leaf_node():
            n = n.best_node(box)
        return n
    def adjust(self):
        if len(self.children) > self.bigm:
            self.overflow()
        if self.parent and (len(self.children) < self.lilm):
            self.underflow()
    def divide_children(self):
        children2 = [c for c in self.children]
        self.children = []
        while children2:
            c1 = children2.pop()
            newp = Rtree(self, c1.box)
            newp.children.append(c1)
            c1.parent = newp
            self.children.append(newp)
            if not children2:
                break
            c2 = smallest_merge(children2, newp.box)
            newp.children.append(c2)
            children2.remove(c2)
            c2.parent = newp
            newp.box = merge(c1.box, c2.box)
        self.box = merge(*(c.box for c in self.children))
        self.merge_up(self.box)
        # Leaves are too small, but grow soon.  Probably.
    def underflow(self):
        "Not implemented"
        raise
    def delete(self, box):
        "Not implemented."
        raise


def merge(*boxes):
    "new box surrounding inputs"
    fns = (min, min, max, max)
    return tuple(f(p) for f,p in zip(fns, zip(*boxes)))

def area(box):
    return box[2]-box[0] * box[3]-box[1]

def smallest_merge(rt_nodes, box):
    "return best node from nodes"
    return min((area(merge(n.box, box)), n) for n in rt_nodes)[1]



