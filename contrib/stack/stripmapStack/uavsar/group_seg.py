#!/usr/bin/env python3

############################################################
# Script to from UAVSAR SLC xmls and vrts using isce.      #
# Modified by Talib Oliver, 2021                           #
############################################################

usage = """
Usage: group_segments.py directory [outfile]

Find all the SLC segments in the given directory and write a JSON file mapping
each image ID to its segments and annotation file.

It's not required that you have all available image segments, but an error will
be raised if any image has a different set of segments from the rest (in order
to trap download errors).
"""

import json
import os
import re
import sys
import glob

# Regular expression for a member of a UAVSAR SLC stack.
# Matches .slc and .ann files.
member_pattern = re.compile(r"""
    (?P<site_name>   ^\w+)_
    (?P<flight_line>  \d{3}\w{2})_
    (?P<flight>       \d{5})_
    (?P<data_take>    \d{3})_
    (?P<date>         \d{6})_
    (?P<band>         \w)
    (?P<angle>        \d{3})
    (?P<polarization> \w{2})_
    (?P<version>      \d{2})_
    (?P<baseest>      \w{2})_
    s(?P<segment>     \d+)_
    (?P<looks_rg>     \d+)x
    (?P<looks_az>     \d+)
    (?P<suffix>       .*)
""", re.VERBOSE)

def find_slcs():
    """Return a list of UAVSAR SLC files in the current directory.
    Raises an exception if not all SLCs belong to the same stack.
    """
    files = os.listdir(os.curdir)
    uav_files = [f for f in files if member_pattern.match(f)]
    slc_files = [f for f in uav_files if f.endswith('.slc')]
    # Make sure they all come from the same stack.
    criteria = ['site_name', 'flight_line', 'version']
    first = member_pattern.match(slc_files[0])
    for slc in slc_files:
        m = member_pattern.match(slc)
        allmatch = True
        for field in criteria:
            allmatch = allmatch and m.group(field) == first.group(field)
        if not allmatch:
            raise ValueError("SLC doesn't match: "+slc)
    return slc_files

def sort_slc_segments(slcs):
    """Given a list of SLC files, return a list of dicts where the SLCs
    are grouped by data take.  Sorted by date, e.g.
        [{'1':slc1_seg1, '2':slc1_seg2}, ..., {'1':slcN_seg1, '2':slcN_seg2}]
    Raises an exception if each group does not have the same set of segments.
    """
    # Initially use a dictionary keyed by flight+datatake to group segments.
    def hash_slc(name):
        m = member_pattern.match(slc)
        return m.group('flight') + m.group('data_take')
    d = dict()
    for slc in slcs:
        key = hash_slc(slc)
        if not d.__contains__(key):
            d[key] = [slc]
        else:
            d[key].append(slc)
    # Now generate the main list.  Sorting by flight+datatake should be okay.
    def seg_id(slc):
        return member_pattern.match(slc).group('segment')
    out = list()
    for key in sorted(d):
        out.append(dict((seg_id(slc),slc) for slc in d[key]))
    # Make sure every data take has the same set of segments.
    segs = set(out[0].keys())
    for group in out:
        if set(group.keys()) != segs:
            raise ValueError('Inconsistent sets of segments. Download okay?')
    return out

def get_ann(slc):
    """Get the annotation file associated with an SLC based on file names.
    """
    m = member_pattern.match(slc)
    groups = 'segment looks_rg looks_az suffix'.split()
    suffix = '_s%s_%sx%s%s' % tuple([m.group(g) for g in groups])
    assert suffix in slc, 'String formatting error.'
    ann = slc.replace(suffix, '.ann')
    if not os.path.exists(ann):
        raise IOError("Missing annotation file: "+ann)
    return ann

def slc_id(slc, ann):
    """Given the name of an SLC and its annotation file,
    return a unique identifier.
    """
    # Get the date from the filename.
    m = member_pattern.match(slc)
    date = m.group('date')
    # Also need hour to disambiguate lines repeated in the same flight.
    # Have to get this from the annotation file.
    # Parse the annotation file in an ad-hoc manner.  Avoid RDF module for now.
    time = None
    for line in open(ann):
        if line.startswith('Start Time of Acquisition'):
            val = line.split('=')[1]
            time = val.split()[1]
    assert time is not None, 'Failed to parse annotation file.'
    #print("20" + date +"T"+time[:2]+time[3:5]) ## Desired format for mintpy
    #return date + time[:5]
    return "20" + date +"T"+time[:2]+time[3:5] ## Desired format for mintpy

def group_segments(dir):
    """Given a directory containing .slc and .ann files for a stack, return
    a data structure of the form
        {
            '2015110112': {
                'annotation': 'foo.ann',
                'segments': {'1':'foo1.slc', '2':'foo2.slc', ...}
            }, ...
        }
    namely a mapping of image IDs (YYYYMMDDhh) to the corresponding
    annotation file and SLC segment file names.
    """
    startdir = os.getcwd()
    os.chdir(dir)
    images = {}
    for segs in sort_slc_segments(find_slcs()):
        slcs = list(segs.values())
        ann = get_ann(slcs[0])
        id = slc_id(slcs[0], ann)
        images[id] = {'annotation': ann, 'segments': segs}
    os.chdir(startdir)
    return images


def main(argv):
    if len(argv) < 2:
        print (usage)
        sys.exit(1)
    dir = argv[1]
    outfile = sys.stdout
    if len(argv) > 2:
        outfile = open(argv[2], 'w')

    images = group_segments(dir)
    json.dump(images, outfile, indent=2, sort_keys=True)


if __name__ == '__main__':
    main(sys.argv)
