"""
Main file to run Geosimilarity CLI.
"""
import click
import geopandas as gpd

from similarity import similarity
from tabulate import tabulate

@click.command()
@click.argument('filepath1')
@click.argument('filepath2')
@click.option('--rf', help='Filepath to store result dataframe.')
@click.option('--how', default='sindex', help='\'sindex\' to merge \
GeoDataFrames on spatial index, \'cartesian\' to merge by cartesian product.')
@click.option('--drop_zeroes', default=False, help='If True, rows in the result\
 GeoDataFrame with a similarity_score of 0 will be dropped.')
@click.option('--keep_geom', default='left', help='\'left\' and \'right\' to \
set geometry column in result GeoDataFrame to df1\'s and df2\'s original \
geometry column, respectively.')
@click.option('--method', default='frechet_dist', help='Which similarity \
measure to use calculate similarity_score. Currently supports \'frechet_dist\'')
@click.option('--precision', default=6, help='Decimal precision to round \
similarity_score. Default=6.')
@click.option('--clip', default=True, help='If True, the similarity_score will \
be calculated based on the clipped portion of the original geometries within \
the intersection of each geometry\'s bounding box. If False, the \
similarity_score will compare the entirety of the original geometries.')
@click.option('--clip_max', default=0.5, help='The minimum ratio of length of \
the clipped geometry to the length of the original geometry, at which to return\
 a non-zero similarity_score.')
def run_similarity(
            filepath1,
            filepath2,
            rf='',
            how='sindex',
            **kwargs,
        ):
    df1 = gpd.read_file(filepath1)
    df2 = gpd.read_file(filepath2)
    result = similarity(df1, df2, how, **kwargs)
    print(tabulate(result, headers='keys', tablefmt='psql'))

    if rf:
        # TODO: Save to shapefile (which only allows one geometry column)
        result.to_csv(rf)
        print('Result saved to %s' % rf)

if __name__ == '__main__':
    run_similarity()
