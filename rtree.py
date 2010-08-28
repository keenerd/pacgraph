#! /usr/bin/env python

from itertools import *

# 629 nodes: 90.28 -> 83.62 -> 53.78
# 3526 nodes: 2897.06 -> 2664.81

def flatten(list_of_lists):
    return list(chain(*list_of_lists))

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
    return cr(r1x, r2x) and cr(r1y, r2y)




class Node(object):
    "Why?  Pyrtree is insert-then-query (but mine has no delete), Rtree has crazy C deps."
    def __init__(self, parent=None, bbox=None, name=None):
        "Only root has no parent, only leaves have names."
        # Half an R-tree.  Not height balanced!  Missing delete().
        bigm = 5
        self.parent = parent
        self.name = name
        self.bigm = bigm
        self.lilm = bigm//2
        self.children = []
        self.bbox = (0,0,0,0)
        if bbox:
            self.bbox = tuple(bbox)
    def show(self, depth=0):
        head = '  ' * depth + str(self.bbox) + ' '
        if self.name:
            return head + self.name + '\n'
        return head + '\n' + ''.join(c.show(depth+1) for c in self.children)
    def root(self):
        if self.parent is None:
            return self
        return self.parent.root()
    def best_node(self, to_add):
        "smallest place for bbox to_add, does not change anything"
        return min((area(merge(to_add, c.bbox)), c) for c in self.children)[1]
    def search(self, bbox=None):
        "yields matching leaf objects, no bbox for all leaves"
        #print 'search', bbox
        todo = [self]
        while todo:
            node = todo.pop()
            if bbox and not in_box(node.bbox, bbox):
                continue
            if node.name:
                yield node
            todo.extend(node.children)
    def insert(self, bbox, name=None):
        #print 'insert', bbox, name
        parent = self.choose_leaf(bbox)
        parent.children.append(Node(parent, bbox, name))
        parent.merge_up(bbox)
        if len(parent.children) > parent.bigm:
            parent.divide_children()
        #print self.root().show()
    def merge_up(self, bbox):
        new_bbox = merge(self.bbox, bbox)
        if new_bbox == self.bbox:
            return
        self.bbox = new_bbox
        if self.parent:
            self.parent.merge_up(self.bbox)
    def is_leaf_node(self):
        return (not self.children) or bool(self.children[0].name)
    def choose_leaf(self, bbox):
        n = self.root()
        while not n.is_leaf_node():
            n = n.best_node(bbox)
        return n
    def adjust(self):
        if len(self.children) > self.bigm:
            self.overflow()
        if self.parent and (len(self.children) < self.lilm):
            self.underflow()
    def divide_children(self):
        #print 'dividing', [c.name for c in self.children], 'into', 
        by_sizes = [(area(c.bbox), c) for c in self.children]
        by_sizes.sort()
        by_sizes = list(zip(*by_sizes)[1])
        # two biggest
        c1 = by_sizes.pop()
        c2 = by_sizes.pop()
        # quasi insert
        p1 = Node(self, c1.bbox)
        p2 = Node(self, c2.bbox)
        p1.children.append(c1)
        p2.children.append(c2)
        # preserve root object
        self.children = [p1, p2]
        while by_sizes:
            c = smallest_merge(by_sizes, p1.bbox)
            p1.children.append(c)
            p1.merge_up(c.bbox)
            by_sizes.remove(c)
            if not by_sizes:
                break
            c = smallest_merge(by_sizes, p2.bbox)
            p2.children.append(c)
            p2.merge_up(c.bbox)
            by_sizes.remove(c)
        self.bbox = merge(p1.bbox, p2.bbox)
        self.merge_up(self.bbox)
        [c.__setattr__('parent', p1) for c in p1.children]
        [c.__setattr__('parent', p2) for c in p2.children]
        #print [c.name for c in p1.children], [c.name for c in p2.children]
        # self is probably too small, underflow?
    def underflow(self):
        "Not implemented"
        raise
    def delete(self, bbox):
        "Not implemented."
        raise


def merge(*bboxes):
    "new bbox surrounding inputs"
    #print 'merge', bboxes
    fns = (min, min, max, max)
    return tuple(f(p) for f,p in zip(fns, zip(*bboxes)))

def area(bbox):
    return bbox[2]-bbox[0] * bbox[3]-bbox[1]

def smallest_merge(nodes, bbox):
    "return best node from nodes"
    return min((area(merge(n.bbox, bbox)), n) for n in nodes)[1]



