"""
Testing basic functionality of similarity.py
"""

import geopandas as gpd
import geosimilarity

from geosimilarity import similarity
from geosimilarity.similarity import similarity
from shapely.geometry import LineString, MultiLineString

class TestSimilarity:
    df2 = gpd.GeoDataFrame([0], \
        geometry=[MultiLineString([[(0,0),(1,1)],[(5,5),(6,6)]])])

    def test_similarity_identical_linestring_gdf(self):
        df = gpd.GeoDataFrame([0], geometry=[LineString([(0,0),(1,1)])])
        similarity_gdf = similarity(df,df)
        assert len(similarity_gdf[similarity_gdf.similarity_score == 1]) == 1

    def test_sindex_similarity(self):
        df1 = gpd.GeoDataFrame([0], geometry=[LineString([(0,0),(1,1)])])
        df2 = gpd.GeoDataFrame([0], \
            geometry=[MultiLineString([[(0,0),(1,1)],[(5,5),(6,6)]])])
        similarity_gdf = similarity(df1,df2,how='sindex')
        assert len(similarity_gdf) == 1

    def test_cartesian_similarity(self):
        df1 = gpd.GeoDataFrame([0], geometry=[LineString([(0,0),(1,1)])])
        df2 = gpd.GeoDataFrame([0], \
            geometry=[MultiLineString([[(0,0),(1,1)],[(5,5),(6,6)]])])
        similarity_gdf = similarity(df1,df2,how='cartesian')
        assert len(similarity_gdf) == 2
