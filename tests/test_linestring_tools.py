"""
Testing basic functionality of linestring_tools.py
"""

import geopandas as gpd
import geosimilarity

from geosimilarity import linestring_tools
from geosimilarity.linestring_tools \
    import line_to_coords, flatten_multilinestring_df
from shapely.geometry import LineString, MultiLineString

class TestLineStringTools:
    def test_line_to_coords_linestring(self):
        line = LineString([(0,0),(1,1)])
        coords = line_to_coords(line)
        assert coords == [[0, 0], [1, 1]]

    def test_line_to_coords_multlinestring(self):
        multiline = MultiLineString([[(0,0),(1,1)], [(1,1),(2,2)]])
        coords = line_to_coords(multiline)
        assert coords == [[0, 0], [1, 1], [1, 1], [2, 2]]

    def test_flatten_multilinestring_df(self):
        multilinestring = MultiLineString([[(0,0),(1,1)], [(1,1),(2,2)]])
        multilinestring_df = gpd.GeoDataFrame([1], geometry=[multilinestring])
        linestring_df = flatten_multilinestring_df(multilinestring_df)
        assert LineString([(0,0),(1,1)]) in linestring_df.geometry \
                and LineString([(1,1),(2,2)]) in linestring_df.geometry
