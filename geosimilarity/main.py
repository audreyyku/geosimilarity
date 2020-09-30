"""
Main file to run Geosimilarity CLI.
"""
import click
import geopandas as gpd

from compare import compare as _compare
from linestring_tools import line_to_coords as _line_to_coords
from linestring_tools \
    import flatten_multilinestring_df as _flatten_multilinestring_df
from similarity import similarity as _similarity
from tabulate import tabulate
from shapely import wkt


# Redirect to other CLI commands
@click.group()
def run():
  pass


@click.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--method', default='frechet_dist', help='Which similarity \
measure to use calculate similarity_score. Currently supports \'frechet_dist\''\
, type=click.Choice(['frechet_dist']))
@click.option('--precision', default=6, help='Decimal precision to round \
similarity_score. Default=6.')
@click.option('--clip', default=True, help='If True, the similarity_score will \
be calculated based on the clipped portion of the original geometries within \
the intersection of each geometry\'s bounding box. If False, the \
similarity_score will compare the entirety of the original geometries.', \
type=bool)
@click.option('--clip_max', default=0.5, help='The minimum ratio of length of \
the clipped geometry to the length of the original geometry, at which to return\
 a non-zero similarity_score.', type=click.FloatRange(min=0, max=1))
def compare(
            filepath,
            method='frechet_dist',
            precision=6,
            clip=True,
            clip_max=0.5
        ):
    """
    Calls geosimilarity/compare.py using input from the CLI

    Parameters
    ----------
    filepath : string
        Filepath of file containing two lines, each containing one LineString
    method : string
        Must be 'frechet_dist' (more methods implemented later)
        Passed as input to the compare method
    precision : int
        The decimal precision at with to round the similarity score
        Default decimal precision is 6
        Passed as input to the compare method
    clip : bool
        If True, then the LineStrings will be clipped to be within the
            minimum bounding box of line1 and line2
        If False, the similarity measure method will be run on the entirety
            line1 and line2
        Passed as input to the compare method
    clip_max : float
        The maximum portion of the line that can be clipped before returning
        a similarity score of 0.
        Default is 0.5 ("At least one half of the line must be compared.")
        Passed as input to the compare method

    Output
    -------
    Prints result GeoDataFrame as well as file save success/failure messages
    """
    # Open file
    f = open(filepath, "r")

    # Read first LineString
    line1 = wkt.loads(f.readline())
    # Read second LineString
    line2 = wkt.loads(f.readline())
    f.close()

    # Call compare function to calculate similarity_score
    similarity_score = _compare(line1, line2, method, precision, clip, clip_max)
    print('\nThe similarity score between \"{0}\" and \"{1}\" is: \n{2}\n'
        .format(line1, line2, similarity_score))


@click.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--rf', type=click.Path(), help='Filepath to store result \
dataframe.')
@click.option('--max_rows', default=None, help='Max rows of result \
GeoDataFrame to print.', type=int)
def flatten_multilinestring_df(filepath, max_rows=None, rf=''):
    """
    Converts a GeoDataFrame with MultiLineStrings in the geometry column to
    a GeoDataFrame with LineStrings in the geometry column instead.
    Duplicates corresponding column data.
    Resets index, but keeps old index.
    """
    gdf = gpd.read_file(filepath)
    result = _flatten_multilinestring_df(gdf)

    # Print result table
    if max_rows != 0:
        print('\n')
        print(tabulate(result.head(max_rows), headers='keys', tablefmt='psql'))
        print('\n')

    # If result filepath is given by user
    if rf:
        # Result filepath must be either .csv or .shp
        if '.csv' not in rf and '.shp' not in rf:
            print('Result not saved to file.')
            print('Filepath \'{}\' must end in either\'.shp\' or \'.csv\''
                .format(rf))
            return
        elif '.shp' in rf:
            result.to_file(rf)
        elif '.csv' in rf:
            result.to_csv(rf)

        print('Result saved to {}\n'.format(rf))


@click.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--rf', type=click.Path(), help='Filepath to store result \
dataframe.')
def line_to_coords(filepath, rf=''):
    """
    Converts (Multi)LineString to 2d-array of Point coordinates
    """
    # Open file
    f = open(filepath, "r")

    # Read first LineString
    linestring = wkt.loads(f.readline())
    f.close()

    # Call line_to_coords function to convert (Multi)LineString to coordinates
    coords = _line_to_coords(linestring)

    print('\n')
    print('Original LineString: {}'.format(linestring))
    print('Coordinates: {}'.format(coords))
    print('\n')

    if rf:
        res = open(rf, "w")
        res.write(coords)
        res.close()


@click.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--max_rows', default=None, help='Max rows of result \
GeoDataFrame to print.', type=int)
def print_gdf(filepath, max_rows=None):
    """
    Print tabulated GeoDataFrame.
    """
    gdf = gpd.read_file(filepath)
    result = _flatten_multilinestring_df(gdf)
    # Print result table
    if max_rows != 0:
        print('\n')
        print(tabulate(result.head(max_rows), headers='keys', tablefmt='psql'))
        print('\n')

@click.command()
@click.argument('filepath1', type=click.Path(exists=True))
@click.argument('filepath2', type=click.Path(exists=True))
@click.option('--rf', type=click.Path(), help='Filepath to store result \
dataframe.')
@click.option('--drop_col', '-d', default='', multiple=True, \
help='Columns to drop before saving result GeoDataFrame to file (multiple \
columns allowed: -d col1 -d col2).', type=str)
@click.option('--how', default='sindex', help='\'sindex\' to merge \
GeoDataFrames on spatial index, \'cartesian\' to merge by cartesian product.',\
type=click.Choice(['sindex', 'cartesian']))
@click.option('--drop_zeroes', default=False, help='If True, rows in the result\
 GeoDataFrame with a similarity_score of 0 will be dropped.', type=bool)
@click.option('--keep_geom', default='geometry_x', help='\'left\' and \'right\'\
 to set geometry column in result GeoDataFrame to df1\'s and df2\'s original \
geometry column, respectively.', \
type=click.Choice(['geometry_x', 'geometry_y']))
@click.option('--max_rows', default=None, help='Max rows of result \
GeoDataFrame to print.', type=int)
@click.option('--method', default='frechet_dist', help='Which similarity \
measure to use calculate similarity_score. Currently supports \'frechet_dist\''\
, type=click.Choice(['frechet_dist']))
@click.option('--precision', default=6, help='Decimal precision to round \
similarity_score. Default=6.', type=int)
@click.option('--clip', default=True, help='If True, the similarity_score will \
be calculated based on the clipped portion of the original geometries within \
the intersection of each geometry\'s bounding box. If False, the \
similarity_score will compare the entirety of the original geometries.', \
type=bool)
@click.option('--clip_max', default=0.5, help='The minimum ratio of length of \
the clipped geometry to the length of the original geometry, at which to return\
 a non-zero similarity_score.', type=click.FloatRange(min=0, max=1))
def similarity(
            filepath1,
            filepath2,
            rf='',
            drop_col='',
            how='sindex',
            keep_geom='geometry_x',
            max_rows=None,
            **kwargs,
        ):
    """
    Calls geosimilarity/similarity.py using input from the CLI

    Parameters
    ----------
    filepath1 : string
        Filepath of first GeoDataFrame
    filepath2 : string
        Filepath of second GeoDataFrame
    rf : string
        Filepath of where to store result GeoDataFrame. Must end in either .csv
        or .shp
    max_rows : int or None
        Maximum number of rows of the result GeoDataFrame to print
    drop_col: string
        Columns to drop before saving result GeoDataFrame to file (multiple
        columns allowed: -d col1 -d col2)
    how : string
        Either 'sindex' or 'cartesian'
        Passed as input to the similarity method
    keep_geom : string
        Either 'geometry_x' or 'geometry_y', indicating which geometry column
        (from df1 and df2 respectively) to use in the returned GeoDataFrame
        Passed as input to the similarity method

    Output
    -------
    Prints result GeoDataFrame as well as file save success/failure messages
    """

    # Read GeoDataFrames
    df1 = gpd.read_file(filepath1)
    df2 = gpd.read_file(filepath2)

    # keep_geom must be set to the geometry column that is not dropped
    if 'geometry_x' in list(drop_col):
        keep_geom = 'geometry_y'
    if 'geometry_y' in list(drop_col):
        keep_geom = 'geometry_x'

    # Call similarity function
    result = _similarity(df1, df2, how, keep_geom, **kwargs)

    # Drop columns if drop_col provided from user
    if len(list(drop_col)) > 0:
        result = result.drop(columns=list(drop_col), axis=1)
        print('Columns {} dropped from result.'.format(list(drop_col)))

    # Print result table
    if max_rows != 0:
        print('\n')
        print(tabulate(result.head(max_rows), headers='keys', tablefmt='psql'))

    # If result filepath is given by user
    if rf:
        # Result filepath must be either .csv or .shp
        if '.csv' not in rf and '.shp' not in rf:
            print('Result not saved to file.')
            print('Filepath \'{}\' must end in either\'.shp\' or \'.csv\''
                .format(rf))
            return
        elif '.shp' in rf:
            # Ensure result table does not contain two geometry columns if
            # result filepath is a shapefile
            if ('geometry_x' in result.columns) \
                and ('geometry_y' in result.columns):
                print('Result not saved to file.')
                print('Only one geometry column is allowed to save to *.shp.')
                print('Please set --drop_col (-d) to either {} or {}.'
                    .format('geometry_x', 'geometry_y'))
                print('\n')
                return
            else:
                # Save result to file
                result.to_file(rf)
        elif '.csv' in rf:
            # Save result to csv
            result.to_csv(rf)
        print('Result saved to {}'.format(rf))
    print('\n')

run.add_command(compare)
run.add_command(flatten_multilinestring_df)
run.add_command(line_to_coords)
run.add_command(print_gdf)
run.add_command(similarity)

if __name__ == '__main__':
    run()
