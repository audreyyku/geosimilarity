import pandas as pd
from shapely.geometry import LineString, LinearRing, MultiLineString

def line_to_coords(linestring):
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
    if linestring is None:
        raise ValueError(
            "Expected geometry type to be in '{0}' but got '{1}'"
            .format(None, allowed_types)
        )

    # Convert LineStrings to coordinates
    if linestring.type in ['LineString', 'LinearRing']:
        coords = [list(point) for point in linestring.coords]

    # Convert MultiLineStrings to coordinates
    elif linestring.type in ['MultiLineString']:
        multiline_coords = [list(line.coords) for line in linestring]
        # Flatten into list of coordinates
        coords = [list(point) for line in multiline_coords
                              for point in line]
    else:
        raise ValueError(
            "Expected geometry type to be in '{1}' but got '{0}'"
            .format(linestring.type, allowed_types)
        )

    return coords


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
            [(index, l) for index, ml in enumerate(df.geometry) \
                        if type(ml) == MultiLineString for l in ml] + \
            # Ignore rows that already contain LineStrings
            [(index, l) for index, l in enumerate(df.geometry) \
                        if type(l) in [LineString, LinearRing]] \
            , columns = ['index', 'geometry'])
        .set_index('index')).reset_index()
