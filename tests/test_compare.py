"""
Testing basic functionality of compare.py
"""

import geosimilarity

from geosimilarity import compare
from geosimilarity.compare import compare
from shapely.geometry import LineString, MultiLineString

class TestCompare:
    def test_compare_identical_linestrings(self):
        line = LineString([(0,0), (1,1)])
        assert compare(line, line) == 1

    def test_compare_identical_multlinestrings(self):
        multiline = MultiLineString([[(0,0),(1,1)], [(1,1),(2,2)]])
        assert compare(multiline, multiline) == 1

    def test_compare_different_linetrings(self):
        line1 = LineString([(0,0), (1,1)])
        line2 = LineString([(0,0.5), (1,1.5)])
        similarity = compare(line1, line2)
        assert similarity < 1 and similarity > 0

    def test_compare_precision(self):
        line1 = LineString([(0,0), (1,1)])
        line2 = LineString([(0.5,0.5), (1.5,1.5)])
        similarity = compare(line1, line2, precision=1)
        assert similarity == 1 or similarity == 0

    def test_compare_no_clip(self):
        line1 = LineString([(0,0), (1,1)])
        line2 = LineString([(0,0), (2,2)])
        similarity = compare(line1, line2, clip=False)
        assert similarity < 1 and similarity > 0

    def test_compare_clip_max1(self):
        line1 = LineString([(0,0), (1,1)])
        line2 = LineString([(0,0), (2,2)])
        similarity = compare(line1, line2, clip_max=0.7)
        assert similarity == 0

    def test_compare_clip_max2(self):
        line1 = LineString([(0,0), (1,1)])
        line2 = LineString([(0,0), (2,2)])
        similarity = compare(line1, line2, clip_max=0.2)
        assert similarity == 1
