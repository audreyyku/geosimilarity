import geopandas as gpd
import pandas as pd
from compare import compare
from crossjoin import df_crossjoin
from linestring_tools import flatten_multilinestring_df
from shapely.geometry import LineString, LinearRing, MultiLineString

def cartesian_similarity(df1, df2, keep_geom='geometry_x', **kwargs):
    """
    Computes Cartesian product of df1 and df2, and calculates the
    similarity_score for each row.

    Parameters
    ----------
    df1 : GeoDataFrame
    df2 : GeoDataFrame
    keep_geom : string
        Either 'geometry_x' or 'geometry_y', indicating which geometry column
        (from df1 and df2 respectively) to use in the returned GeoDataFrame

    Returns
    -------
    res : GeoDataFrame
        Cartesian product of df1 and df2 with a new similarity_score column
    """

    # Perform Cartesian product
    res = df_crossjoin(df1, df2)

    # Map compare function on every row prduced by the Cartesian product
    res['similarity_score'] = \
        res[['geometry_x', 'geometry_y']].apply(
            lambda x: compare(x['geometry_x'], x['geometry_y'], **kwargs), \
        axis=1)

    return gpd.GeoDataFrame(res, geometry=keep_geom)

def sindex_similarity(df1, df2, keep_geom='geometry_x', **kwargs):
    """
    Merges df1 and df2 based on how the spatial index of df2 intersects with
    the geometry column of df1

    Parameters
    ----------
    df1 : GeoDataFrame
    df2 : GeoDataFrame
    keep_geom : string
        Either 'geometry_x' or 'geometry_y', indicating which geometry column
        (from df1 and df2 respectively) to use in the returned GeoDataFrame

    Returns
    -------
    res : GeoDataFrame
        Merged GeoDataFrame of df1 and df2 with a new
        similarity_score column
    """

    # Combine non-geometry columns of both DataFrames
    cols = [c for c in (list(df2.columns) + list(df1.columns)) \
            if c != 'geometry']

    # Add suffix to duplicate columns
    if len(cols) != len(set(cols)):
        df1 = df1.add_suffix('_x')
        df2 = df2.add_suffix('_y')
    else:
        df1 = df1.rename({'geometry':'geometry_x'})
        df2 = df1.rename({'geometry':'geometry_y'})

    df1 = df1.set_geometry('geometry_x')
    df2 = df2.set_geometry('geometry_y')

    # Create empty result DataFrame
    res = pd.DataFrame(columns = \
                       (list(df2.columns) + list(df1.columns) \
                        + ['similarity_score',
                           '__idx1',
                           '__idx2',
        ])).set_index(['__idx1', '__idx2'])

    # Get the R-tree spatial index of df2 (and corresponding bounding boxes)
    spatial_index = df2.sindex

    # Iterate through each row of df1 to find all possible matches with df2
    for idx1, row1 in df1.iterrows():
        #Get intersecting bounding boxes of df2
        possible_matches_index = \
            list(spatial_index.intersection(row1.geometry_x.bounds))
        possible_matches = df2.iloc[possible_matches_index]

        # Compute similarity between all possible matches and row1
        for idx2, row2 in possible_matches.iterrows():
            # Create DataFrame row combining row1 and row2
            intersect = pd.concat([row1, row2], axis = 0)

            # Compute similarity_score between row1 and row2
            intersect['similarity_score'] = compare(row1.geometry_x, \
                                                    row2.geometry_y, **kwargs)

            # Insert row into result DataFrame
            res.loc[(idx1, idx2),:] = intersect

    return gpd.GeoDataFrame(res, geometry=keep_geom)

def similarity(
            df1,
            df2,
            how='sindex',
            keep_geom='geometry_x',
            drop_zeroes=False,
            **kwargs
        ):
    """
    Computes similarity between geometries of two GeoDataFrames.

    Currently only supports data GeoDataFrames with (Multi)LineStrings.

    Parameters
    ----------
    df1 : GeoDataFrame
    df2 : GeoDataFrame
    how : string
        Either 'sindex' or 'cartesian'. Determines whether joining df1 and
        df2 will be performed by intersecting Spatial Index bounding boxes
        or by getting the Cartesian product of df1 and df2.
    keep_geom : string
        Either 'geometry_x' or 'geometry_y', indicating which geometry column
        (from df1 and df2 respectively) to use in the returned GeoDataFrame
    drop_zeroes : bool
        If True, the rows in the returned GeoDataFrame with a similarity
        score of 0 will be dropped.

    Returns
    -------
    df : GeoDataFrame
        GeoDataFrame with the columns of both df1 and df2 with a new columns
        containing the similarity score, multi-indexed by the original
        indices of df1 and df2.
    """

    allowed_hows = [
        'cartesian',
        'sindex',
    ]

    # Null/Type check input
    if df1.empty or df2.empty:
        raise ValueError(
            "GeoDataFrames were Null"
        )

    if type(df1) != gpd.GeoDataFrame or type(df2) != gpd.GeoDataFrame:
        raise ValueError(
            "GeoDataFrames expected but received '{}'"
            .format([type(df1), type(df2)])
        )

    # Check that the CRS is the same
    if df1.crs != df2.crs:
        raise ValueError(
            "CRS must be equal for `df1` and `df2` but instead \
            were '{0}' and '{1}'"
            .format(df1.crs, df2.crs)
        )

    # Validate that the GeoDataFrames inputted only contain LineString
    # geometry types
    polys = ["Polygon", "MultiPolygon"]
    lines = ["LineString", "MultiLineString", "LinearRing"]
    points = ["Point", "MultiPoint"]
    for i, df in enumerate([df1, df2]):
        poly_check = df.geom_type.isin(polys).any()
        lines_check = df.geom_type.isin(lines).any()
        points_check = df.geom_type.isin(points).any()
        if sum([poly_check, points_check]) >= 1:
            raise NotImplementedError(
                "df{0} contains geometry types other than '{1}'"
                .format(i + 1, lines)
            )
        if sum([poly_check, lines_check, points_check]) > 1:
            raise NotImplementedError(
                "df{} contains mixed geometry types.".format(i + 1)
            )

    # Flatten MultiLineString GeoDataFrames to only contain LineStrings
    if df1.geom_type.isin(["MultiLineString"]).any():
        df1 = flatten_multilinestring_df(df1)
    if df2.geom_type.isin(["MultiLineString"]).any():
        df2 = flatten_multilinestring_df(df2)

    # Approach 1: Get Cartesian product
    if how == 'cartesian':
        res =  cartesian_similarity(df1, df2, keep_geom, **kwargs)
    # Approach 2: R-tree spatial index merge
    elif how == 'sindex':
        res = sindex_similarity(df1, df2, keep_geom, **kwargs)
    else:
        raise ValueError(
            "`how` was '{0}' but is expected to be in {1}"
            .format(how, allowed_hows)
        )

    if drop_zeroes == True:
        # Drop rows of resulting GeoDataFrame that have
        # a similarity_score of 0
        res = res[res['similarity_score'] != 0]

    return res
