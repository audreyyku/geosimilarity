"""
Main file to run Geosimilarity CLI.
"""
import click
import geopandas as gpd

from similarity import similarity
from tabulate import tabulate

@click.command()
@click.option('--filepath1', prompt='Filepath of the first dataframe')
@click.option('--filepath2', prompt='Filepath of the second dataframe')
@click.option('--result_filepath', prompt='Filepath to store result dataframe')
def run_similarity(filepath1, filepath2, result_filepath=''):
    df1 = gpd.read_file(filepath1)
    df2 = gpd.read_file(filepath1)
    result = similarity(df1, df2)
    print(tabulate(result, headers='keys', tablefmt='psql'))
    if result_filepath:
        # TODO: Save to shapefile (which only allows one geometry column)
        result.to_csv(result_filepath)

if __name__ == '__main__':
    run_similarity()
