# geosimilarity.py

from class_cli import CLI

import math
import numpy as np
import pandas as pd
import pygeos
import similaritymeasures as sm
from shapely.geometry import LineString, LinearRing, MultiLineString

cli = CLI()

@cli.Program()
class GeoSimilarity:

    def line_to_coords(line):
        """
        Converts (Multi)LineString to 2d-array of Point coordinates

        Parameters
        ----------
        line : (Multi)LineString

        Returns
        -------
        coords : list
            List of points representing the endpoints of the (Multi)LineStrings
        """

        allowed_types = [
            'LineString',
            'LinearRing',
            'MultiLineString',
        ]

        coords = []

        # Null check
        if line is None:
            raise ValueError(
                "Expected geometry type to be in '{0}' but got '{1}'"
                .format(None, allowed_types)
            )

        # Convert LineStrings to coordinates
        if line.type.isin(['LineString', 'LinearRing']):
            coords = [list(point) for point in line.coords]

        # Convert MultiLineStrings to coordinates
        elif line.type.isin(['MultiLineString']):
            multiline_coords = [list(line.coords) for line in route]
            # Flatten into list of coordinates
            coords = [list(point) for line in multiline_coords
                                  for point in line]
        else:
            raise ValueError(
                "Expected geometry type to be in '{1}' but got '{0}'"
                .format(line.type, allowed_types)
            )

        return coords

    def df_crossjoin(df1, df2, **kwargs):
        """
        From: https://gist.github.com/internaut/5a653317688b14fd0fc67214c1352831
        Make a cross join (cartesian product) between two dataframes by using a
        constant temporary key. Also sets a MultiIndex which is the cartesian
        product of the indices of the input dataframes.
        See: https://github.com/pydata/pandas/issues/5401

        Parameters
        ----------
        df1 : DataFrame
        df2 : DataFrame
        kwargs : keyword arguments that will be passed to pd.merge()

        Returns
        -------
        res : DataFrame
            Cartesian join of df1 and df2
        """

        # Create temporary key to merge the DataFrames on
        df1['_tmpkey'] = 1
        df2['_tmpkey'] = 1

        # Merge DataFrames and create MultiIndex
        res = pd.merge(df1, df2, on='_tmpkey', **kwargs).drop('_tmpkey', axis=1)
        res.index = pd.MultiIndex.from_product((df1.index, df2.index))

        # Drop temporary key
        df1.drop('_tmpkey', axis=1, inplace=True)
        df2.drop('_tmpkey', axis=1, inplace=True)

        return res

    def flatten_multilinestring_df(df):
        """
        Converts a GeoDataFrame with MultiLineStrings in the geometry column to
        a GeoDataFrame with LineStrings in the geometry column instead.
        Duplicates corresponding column data.
        Resets index, but keeps old index.

        Parameters
        ----------
        df : GeoDataFrame of MultiLineStrings (and LineStrings)

        Returns
        -------
        res : GeoDataFrame of LineStrings

        """
        return df.drop(columns = ['geometry'], axis = 1).join(
            pd.DataFrame(
                [(index, l) for index, ml in enumerate(bus.geometry) \
                            if type(ml) == MultiLineString for l in ml] + \
                # Ignore rows that already contain LineStrings
                [(index, l) for index, l in enumerate(bus.geometry) \
                            if type(l) in [LineString, LinearRing]] \
                , columns = ['index', 'geometry'])
            .set_index('index')).reset_index()

    @cli.Operation()
    def compare(
            line1,
            line2,
            method='frechet_dist',
            precision=6,
            clip=True,
            clip_max=0.5
        ):

        """
        Compute similarity between two (Multi)LineStrings.
        Returns value 0.0 (completely dissimilar) to 1.0 (completely similar)
        Based on Frechet distance

        Parameters
        ----------
        line1 : (Multi)LineString
        line2 : (Multi)LineString
        method : string
            Must be 'frechet_dist' (more methods implemented later)
        precision : int
            The decimal precision at with to round the similarity score
            Default decimal precision is 6.
        clip : bool
            If True, then the LineStrings will be clipped to be within the
                minimum bounding box of line1 and line2
            If False, the similarity measure method will be run on the entirety
                line1 and line2
        clip_max : float
            The maximum portion of the line that can be clipped before returning
            a similarity score of 0.
            Default is 0.5 ("At least one half of the line must be compared.")

        Returns
        -------
        similarity_score : float
            Returns value 0.0 (completely dissimilar) to
            1.0 (completely similar)

        """

        allowed_methods = [
            'frechet_dist',
        ]

        if (clip == True):
            # Bounding box of line1
            box1 = line1.bounds
            box1_left = box1[0]
            box1_bottom = box1[1]
            box1_right = box1[2]
            box1_top = box1[3]

            # Bounding box of line1
            box2 = line2.bounds
            box2_left = box2[0]
            box2_bottom = box2[1]
            box2_right = box2[2]
            box2_top = box2[3]

            # Gives bottom-left point of intersection rectangle
            left = max(box1_left, box2_left)
            bottom = max(box1_bottom, box2_bottom)

            # Gives top-right point of intersection rectangle
            right = min(box1_right, box2_right)
            top = min(box1_top, box2_top)

            # No intersecting bounding box
            if (left > right or bottom > top) :
                return 0

            # Create minimum bounding box
            min_box = Polygon([(left, bottom), (left, top), (right, top), \
                               (right, bottom), (left, bottom)])

            # Clip lines to be within minimum bounding box
            clipped1 = line1.intersection(min_box)
            clipped2 = line1.intersection(min_box)

            # Line does not intersect minimum bounding box
            if (clipped1.is_empty or clipped2.is_empty):
                return 0

            # In this case, the resulting clipped lines do not accurately
            # represent the similarity between the original lines
            if (clipped1.length < line1.length*clip_max
                    and clipped2.length < line2.length*clip_max):
                return 0

            # Convert to discrete coordinates to input into similarity
            # measure method
            coords1 = line_to_coords(clipped1)
            coords2 = line_to_coords(clipped2)

        else:
            coords1 = line_to_coords(line1)
            coords2 = line_to_coords(line2)

        if method == 'frechet_dist':
            # Formula: e^(-frechet_dist/line1.length)
            return round(math.exp((-1)*sm.frechet_dist(coords1, coords2) \
                        /line1.length), precision)
        else:
            return "`method` must be in '{0}''".format(allowed_methods)

    def cartesian_similarity(df1, df2, keep_geom='left', **kwargs):
        """
        Computes Cartesian product of df1 and df2, and calculates the
        similarity_score for each row.

        Parameters
        ----------
        df1 : GeoDataFrame
        df2 : GeoDataFrame
        how : string
        keep_geom : string
            Either 'left' or 'right', indicating which geometry column (from df1
            and df2 respectively) to use in the returned GeoDataFrame

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

        return gpd.GeoDataFrame(res, geometry = ('geometry_x' \
                                if keep_geom == 'left' else 'geometry_y'))

    def sindex_similarity(df1, df2, keep_geom='left', **kwargs):
        """
        Merges df1 and df2 based on how the spatial index of df2 intersects with
        the geometry column of df1

        Parameters
        ----------
        df1 : GeoDataFrame
        df2 : GeoDataFrame
        how : string
        keep_geom : string
            Either 'left' or 'right', indicating which geometry column (from df1
            and df2 respectively) to use in the returned GeoDataFrame

        Returns
        -------
        res : GeoDataFrame
            Merged GeoDataFrame of df1 and df2 with a new
            similarity_score column
        """

        # Create empty result DataFrame
        res = pd.DataFrame(columns = (\
                [c for c in (list(df2.columns) + list(df1.columns))
                    if c != 'geometry']
                    + ['similarity_score',
                        'geometry_x',
                        'geometry_y',
                        '__idx1',
                        '__idx2',
                ])).set_index(['__idx1', '__idx2'])

        # Get the R-tree spatial index of df2 (and corresponding bounding boxes)
        spatial_index = df2.sindex

        # Iterate through each row of df1 to find all possible matches with df2
        for idx1, row1 in df1.iterrows():
            #Get intersecting bounding boxes of df2
            possible_matches_index = \
                list(spatial_index.intersection(row1.geometry.bounds))
            possible_matches = df2.iloc[possible_matches_index]

            # Compute similarity between all possible matches and row1
            row1['geometry_x'] = row1['geometry']
            for idx2, row2 in possible_matches.iterrows():
                row2['geometry_y'] = row2['geometry']

                # Create DataFrame row combining row1 and row2
                intersect = pd.concat([row1.drop(labels=['geometry']), \
                                       row2.drop(labels=['geometry'])], \
                                       axis = 0)

                # Compute similarity_score between row1 and row2
                intersect['similarity_score'] = compare(row1.geometry, \
                                                        row2.geometry, **kwargs)
                # Insert row into result DataFrame
                res.loc[(idx1, idx2),:] = intersect

        return gpd.GeoDataFrame(res, geometry = ('geometry_x'
                                if keep_geom == 'left' else 'geometry_y'))

    @cli.Operation()
    def similarity(df1, df2, how='sindex', drop_zeroes=False):
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
        if df1 == None or df2 == None:
            raise ValueError(
                "GeoDataFrames were Null"
            )
        if type(df1) != GeoDataFrame or type(df2) != GeoDataFrame:
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
            res =  cartesian_similarity(df1, df2, **kwargs)
        # Approach 2: R-tree spatial index merge
        elif how == 'sindex':
            res = sindex_similarity(df1, df2, **kwargs)
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

if __name__ == "__main__":
    GeoSimilarity().CLI.main()
