#! /usr/bin/env python

import random, math, subprocess, os, copy
from optparse import OptionParser
from itertools import *
from collections import deque, defaultdict

# depends contains %CONFLICTS%, 
# %DEPENDS%, %OPTDEPENDS%, %PROVIDES%

# desc contains %URL%, %REPLACES%, %LICENSE%,
# %NAME%, %GROUPS%, %BUILDDATE%, %REASON%, %DESC%,
# %SIZE%, %PACKAGER%, %ARCH%, %INSTALLDATE%, %VERSION%

pj = os.path.join

# start ArchLinux specific code
pac_dir = "/var/lib/pacman/local/"

def l_part(n, c):
    return n.partition(c)[0]

def reduce_by(fn, data, arg_list):
    data = fn(data, arg_list.pop(0))
    if not arg_list:
        return data
    return reduce_by(fn, data, arg_list)

def clean(n):
    n = n.strip()
    return reduce_by(l_part, n, list('><:='))

def load_info(file):
    info = {}
    mode = None
    for line in file:
        line = clean(line)
        if not line:
            continue
        if line.startswith('%'):
            mode = line
            info[mode] = []
            continue
        info[mode].append(line)
    file.close()
    return info

def strip_info(info):
    keep = ['DEPENDS', 'OPTDEPENDS', 'PROVIDES', 'SIZE']
    info = dict((k.strip('%'),v) for k,v in info.iteritems())
    name = info['NAME'][0]
    info = dict((k,v) for k,v in info.iteritems() if k in keep)
    if 'SIZE' in info:
        info['SIZE'] = int(info['SIZE'][0], 10)
    else:
        info['SIZE'] = 0
    return name, info

def load_tree():
    packages = [p for p,d,f in os.walk(pac_dir) if f]
    tree = {}
    for p in packages:
        info = {}
        file = open(pj(p,'depends'), 'r')
        info.update(load_info(file))
        file = open(pj(p,'desc'), 'r')
        info.update(load_info(file))
        try:
            name, info = strip_info(info)
            tree[name] = info
        except:
            print 'Error reading package', p
    return tree

def search_provides(package, tree):
    "use only on load_tree data"
    tree2 = dict((p,tree[p]['PROVIDES']) for p in tree if 'PROVIDES' in tree[p])
    return [p for p in tree2 if package in tree2[p]]

def actually_installed(packages, tree):
    "use only on load_tree data"
    simple = set(packages) & set(tree.keys())
    maybe = set(packages) - simple
    for p in maybe:
        provides = search_provides(p, tree)
        if len(provides) > 1:
            print 'error:', p, 'found in', provides
        if len(provides) == 1:
            simple.add(provides[0])
        # len 0 means not installed optdep
    return list(simple)

def merge_tree(tree):
    "merge provides, depends, optdepends"
    tree2 = {}
    # merge
    for p in tree:
        tp = defaultdict(list, tree[p])
        deps = tp['DEPENDS'] + tp['OPTDEPENDS']
        # remove unused optdeps
        deps = actually_installed(deps, tree)
        tree2[p] = (tree[p]['SIZE'], deps)
    return tree2
# end ArchLinux specific code

def full_deps(package, tree):
    "returns every package in dep tree"
    deps = set()
    to_crawl = deque([package])
    while to_crawl:
        current = to_crawl.popleft()
        if current in deps:
            continue
        deps.add(current)
        current_deps = set(tree[current][1])
        to_crawl.extend(current_deps - deps)
    return list(deps)

def invert_tree(tree):
    "turns depends-on into required-by"
    reqs = dict((p,(tree[p][0], [])) for p in tree)
    for p in tree:
        deps = tree[p][1]
        [reqs[d][1].append(p) for d in deps]
    return reqs

def flatten(listOfLists):
    return list(chain.from_iterable(listOfLists))

def rle(m):
    return [(n, len(list(g))) for n,g in groupby(m)]

def single_depends(tree):
    "packages with only one parent"
    all_deps = flatten(v[1] for k,v in tree.iteritems())
    dep_count = dict(rle(sorted(all_deps)))
    return (k for k,v in dep_count.iteritems() if v == 1)

def compress_chains(tree):
    "single depends are absorbed into parent"
    while True:
        singles = single_depends(tree)
        try:
            s = singles.next()
        except StopIteration:
            return tree
        req_by = invert_tree(tree)
        parent = req_by[s][1][0]
        #print 'merge', s, 'into', parent
        new_size = tree[parent][0] + tree[s][0]
        new_deps = tree[parent][1] + tree[s][1]
        new_deps = list(set(new_deps))
        new_deps.remove(s)
        tree[parent] = (new_size, new_deps)
        tree.pop(s)

def sum_sizes(packages, tree):
    return sum(tree[p][0] for p in packages if p in tree)

def shared_size(package, tree):
    "package and all deps"
    return sum_sizes(full_deps(package, tree), tree)

def biggest_packs(tree):
    packs = [(shared_size(p, tree), p) for p in tree]
    packs.sort()
    packs.reverse()
    return [p for s,p in packs]

def dep_sizes(tree):
    "include deps in size"
    return dict((p, (shared_size(p, tree), tree[p][1])) for p in tree)

def drawable_tree():
    return compress_chains(merge_tree(load_tree()))

def toplevel_packs(tree):
    "do this before bidrection"
    toplevel = set(tree.keys())
    for name in tree:
        deps = tree[name][1]
        toplevel = toplevel - set(deps)
    return toplevel

#print 'worst shared packages:', biggest_packs(tree)[:20]
#print 'most crucial packages:', biggest_packs(invert_tree(tree))[:20]

def bidirection(packs):
    "directed graph -> undirected graph"
    packs2 = dict((n, [(0,0), []]) for n in packs.keys())
    for name in packs:
        dim, links = packs[name]
        packs2[name][0] = dim
        packs2[name][1].extend(links)
        for link in links:
            packs2[link][1].append(name)
    for name in packs2:
        packs2[name][1] = list(set(packs2[name][1]))
    return packs2

def pt_sizes(tree, min_pt=10, max_pt=100):
    "size in bytes -> size in points"
    sizes = [deps[0] for p,deps in tree.iteritems()]
    min_s = min(sizes)
    max_s = max(sizes)
    for p, deps in tree.iteritems():
        size = deps[0]
        pt = int((max_pt-min_pt)*(size-min_s)/(max_s-min_s) + min_pt)
        tree[p] = (pt, tree[p][1])
    return tree

def prioritized(packs):
    "returns list of names, sorted by priority"
    # first are the most 'central'
    stats = [(len(v[1]), k) for k,v in packs.items()]
    stats = [n for l,n in reversed(sorted(stats))]
    # but slip in anyone who's deps are met early
    stats2 = []
    fs = frozenset
    for n in stats:
        if n in stats2:
            continue
        stats2.append(n)
        plotted = fs(stats2)
        deps_met = [k for k,v in packs.items() if fs(v[1]) <= plotted]
        for d in fs(deps_met) - plotted:
            stats2.append(d)
    return stats2

def ran_rad():
    return random.random()*2*math.pi

def bbox(center, dim):
    c,d = center,dim
    x1,x2 = c[0]-d[0]//2, c[0]+d[0]//2
    y1,y2 = c[1]-d[1]//2, c[1]+d[1]//2
    return [x1, y1, x2, y2] 

def common_ranges(r1, r2):
    "returns true if overlap"
    r1,r2 = list(r1), list(r2)
    a = sorted([r1, r2])
    a = a[0] + a[1]
    b = sorted(r1 + r2)
    return a != b

def in_box(bbox1, bbox2):
    cr = common_ranges
    r1x = bbox1[0::2]
    r1y = bbox1[1::2]
    r2x = bbox2[0::2]
    r2y = bbox2[1::2]
    return cr(r1x, r2x) and cr(r1y, r2y)

def all_bboxes(name, coords, pri=None):
    b_list = []
    if pri is None:
        name_list = coords.keys()
    else:
        name_list = pri[:pri.index(name)]
    for n in name_list:
        c,d = coords[n]
        b_list.append(bbox(c,d))
    return b_list

def normalize(point, origin):
    p2 = point[0]-origin[0], point[1]-origin[1]
    length = (p2[0]**2 + p2[1]**2)**0.5
    return p2[0]/length, p2[1]/length

def link_pull(name, origin_n, packs, coords):
    "average of angles of links"
    origin = coords[origin_n][0]
    norm_ps = lambda ps: [normalize(c, origin) for c in ps if c not in [(0,0), origin]] 
    good_links = packs[name][1]
    bad_links  = packs[origin_n][1]
    g_centers  = [coords[l][0] for l in good_links]
    g_centers  = norm_ps(g_centers)
    b_centers  = [coords[l][0] for l in bad_links]
    b_centers  = norm_ps(b_centers)
    b_centers  = [(-x,-y) for x,y in b_centers]
    centers = g_centers + b_centers
    if not centers:  
        # new branch, try to avoid existing branches
        centers = [coords[l][0] for l in coords.keys()]
        centers = norm_ps(centers)
        if not centers:
            return (0,0)
        centers = [(-x,-y) for x,y in centers]
    return sum(zip(*centers)[0]), sum(zip(*centers)[1])

def xy2rad(x,y):
    "adds some wiggle so things are less spindly"
    if (x,y) == (0,0):
        return ran_rad()
    wiggle = 0.35  # radians
    wiggle = random.random()*wiggle - wiggle/2.0
    return math.atan2(y,x) + wiggle

def pol2xy(o,a,r):
    return int(o[0]+r*math.cos(a)), int(o[1]+r*math.sin(a))

def pt2dim(name, pt):
    x_scale = 0.65
    y_scale = 1.50
    return int(len(name)*pt*x_scale), int(pt*y_scale)

def empty_coords(packs):
    return dict((k, [(0,0), pt2dim(k,v[0])]) for k,v in packs.items())

def best_origin(name, pri, packs):
    "returns sibling with most links, or root"
    possible = pri[:pri.index(name)]
    possible = [n for n in possible if n in packs[name][1]]
    if not possible:
        return pri[0]  # root package
    return possible[0]

def place(packs):
    "radial placement algo, returns non-overlapping coords"
    coords = empty_coords(packs)
    # coords = {name: [(x_pos,y_pos), (x_size, y_size)], ...}
    pri = prioritized(packs)
    for name in pri[1:]:
        origin_name = best_origin(name, pri, packs)
        print 'placing', name, 'around', origin_name
        origin = coords[origin_name][0]
        heading = xy2rad(*link_pull(name, origin_name, packs, coords))
        scale = len(packs[name][1])+1  # more links need more room
        step,r = 5*scale,5*scale
        b_list = all_bboxes(name, coords, pri)
        while True:
            coords[name][0] = pol2xy(origin, heading, r)
            bb1 = bbox(*coords[name])
            o = any(in_box(bb1, bb2) for bb2 in b_list)
            #print name, r, step, o
            if o:
                if step < 0:
                    step = step * -1
                step = step * 2
            else:
                if 0 < step < 4*scale:
                    break
                if step > 0:
                    step = step * -1
                step = step // 3
            if -scale < step < 0:
                step = -scale
            if 0 >= step > scale:
                step = scale
            r = abs(r + step)
    return coords

def offset_coord(c,d):
    "corrects textbox origin"
    return c[0]-d[0]//2, c[1]  #+d[1]//2

def xml_wrap(tag, inner, **kwargs):
    kw = ' '.join('%s="%s"' % (k, v) for k,v in kwargs.items())
    if inner is None:
        return '<%s %s/>' % (tag, kw)
    return '<%s %s>%s</%s>' % (tag, kw, inner, tag)

def control_point(p1, p2):
    dx = abs(p2[0] - p1[0])
    lower  = (p1,p2)[p1[1]<p2[1]]
    higher = (p2,p1)[p1[1]<p2[1]]
    return (lower[0]+higher[0])//2, lower[1]+dx//2

def quad_spline(p1, p2):
    "boofor DSL in XML"
    p1,p2 = sorted((p1,p2))
    x1,y1 = p1
    x2,y2 = p2
    xc,yc = control_point(p1, p2)
    return 'M%i,%i Q%i,%i %i,%i' % (x1,y1, xc,yc, x2,y2)

def svg_text(text, center_dim, size):
    p = offset_coord(*center_dim)
    x,y = str(p[0]), str(p[1])
    pt = str(size)
    kw = {'x':x,'y':y,'font-size':pt}
    return xml_wrap('text', text, **kw) 

def svg_spline(point1, point2):
    return xml_wrap('path', None, d=quad_spline(point1, point2))

def all_points(coords):
    "slightly incomplete, clips the splines"
    points = []
    for wbox in all_bboxes(None, coords, None):
        points.append(wbox[:2])
        points.append(wbox[2:])
    return points

def recenter(coords, points):
    "shift everything into quadrant 1"
    xs,ys = zip(*points)
    min_x = min(xs)
    min_y = min(ys)
    for name in coords:
        p = coords[name][0]
        coords[name][0] = p[0]-min_x, p[1]-min_y
    return coords

def window_size(points):
    xs,ys = zip(*points)
    return max(xs)-min(xs), max(ys)-min(ys)

def svgify(packs, coords, toplevel, options):
    text1,text2,paths = [],[],[]
    bottomlevel = set(packs) - toplevel
    all_ps = all_points(coords)
    coords = recenter(coords, all_ps)
    for pack in bottomlevel:
        size,links = packs[pack]
        cd = coords[pack]
        text1.append(svg_text(pack, cd, size))
    for pack in toplevel:
        size, links = packs[pack]
        cd = coords[pack]
        text2.append(svg_text(pack, cd, size))
    for pack in packs:
        size,links = packs[pack]
        p1 = coords[pack][0]
        for link in [l for l in links if l<pack]:
            p2 = coords[link][0]
            paths.append(svg_spline(p1,p2))
    svg = open('pacgraph.svg', 'w')
    svg.write('<svg width="%i" height="%i">\n' % window_size(all_ps))
    svg.write('<g style="stroke:%s; stroke-opacity:0.15; fill:none;">\n' % options.link)
    for path in paths:
        svg.write(path+'\n')
    svg.write('</g>\n')
    svg.write('<g font-family="Monospace" fill="%s">\n' % options.dependency)
    for text in text1:
        svg.write(text+'\n')
    svg.write('</g>\n')
    svg.write('<g font-family="Monospace" fill="%s">\n' % options.toplevel)
    for text in text2:
        svg.write(text+'\n')
    svg.write('</g>\n')
    svg.write('</svg>')
    svg.close()

def call(cmd):
    subprocess.call([cmd], shell=True)

def parse():
    parser = OptionParser()
    parser.add_option('-b', '--background', dest='background', default='#ffffff')
    parser.add_option('-l', '--link', dest='link', default='#606060')
    parser.add_option('-t', '--top', dest='toplevel', default='#0000ff')
    parser.add_option('-d', '--dep', dest='dependency', default='#6a6aa2')
    parser.add_option('-p', '--point', dest='point_size', type='int', nargs=2, default=(10,100))
    parser.add_option('-s', '--svg', dest='svg_only', action='store_true', default=False)
    options, args = parser.parse_args()
    return options

def main():
    options = parse()
    print 'Loading package info'
    tree = drawable_tree()
    tree = pt_sizes(tree, *options.point_size)
    toplevel = toplevel_packs(tree)
    packs = bidirection(tree)
    print 'Placing all packages'
    coords = place(packs)
    print 'Saving SVG'
    svgify(packs, coords, toplevel, options)
    if options.svg_only:
        return
    print 'Rendering SVG'
    if 'inkscape' in tree:
        call('inkscape -D -b "%s" -e pacgraph.png pacgraph.svg' % options.background)
        return
    if 'svg2png' in tree:
        call('svg2png pacgraph.svg pacgraph.png')
        call('mogrify -background white -layers flatten pacgraph.png')
        return
    if 'imagemagick' in tree:
        call('convert pacgraph.svg pacgraph.png')
        return
    print 'No way to convert SVG to PNG.'
    print 'Inkscape, svg2png or imagemagick would be nice.'

if __name__ == "__main__":
    main()

"""
possible/future command line args

-f  --file        output file name
-a  --add         packages
-c  --chains      retain package chains
-d  --dot         load dot file

line weight? alpha? tree dump/load?
"""
