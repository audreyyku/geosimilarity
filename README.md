# Geosimilarity

Computes similarity between geometries of two GeoDataFrames

# Problem to solve:
- Slight differences in geometries can make it difficult to perform certain operations such as ```geopandas.overlay(...)```
- This is especially the case for LineStrings

# Real world context:
- The images below show two GeoDataFrames from two separate data sources, one representing the streets of the City of Oakland (grey) from [OSMnx](https://github.com/gboeing/osmnx) and one representing the bus routes of a city (green) from the [AC Transit website](http://www.actransit.org/bus-route-gis-shape-files/?did=3)
![oakland_bus_routes](images/oakland_bus_routes.png)
- When zoomed in, see how the green and grey lines largely overlap, but have the slightest misalignments
![oakland_bus_routes_clipped](images/oakland_bus_routes_clipped.png)
- These miniscule misalignments can make it so the LineStrings representing the same streets in the physical world are deemed different geometries and thus different streets
- The question at hand is: How can we easily identify which street LineStrings are very similar (and are likely to represent the same street in the physical world)?

# Implementation
- Combines two GeoDataFrames and computes the similarity_score between the geometries of each GeoDataFrame
- The similarity_score, which ranges from 0.0 (completely dissimilar) to 1.0 (completely similar), is determined based on the Frechet distance using the formula ```e^(-frechet/line.length)```
- More on Frechet distance can be found [here](https://en.wikipedia.org/wiki/Fr%C3%A9chet_distance)

# Set up

```
$ git clone https://github.com/ukyerdua/geosimilarity.git
$ cd geosimilarity
$ pip3 install -r requirements.txt
$ export PYTHONPATH="$PWD/geosimilarity"
```

If you do not set the ```PYTHONPATH``` to ```geosimilarity/geosimilarity/```, then the test files will not be able to read the functions to be tested in ```geosimilarity/geosimilarity/*.py```

# Run CLI
## Use --help to see functions (commands) available:

```
$ bin/geosimilarity
```

```
$ bin/geosimilarity
Usage: main.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  compare
  similarity
```

## To run "compare" on two LineStrings

```
$ bin/geosimilarity compare [filepath] [--method='frechet_dist'] [--precision=6] [--clip=True] [--clip_max=0.5]
```

```filepath``` must contain a file containing two lines, each containing a LineString of the following format ```LINESTRING (0 0, 1 1, 2 2)```. See below for example.

**Use --help to see descriptions of options**

```
$ bin/geosimilarity compare --help
```

```
$ bin/geosimilarity compare --help
Usage: main.py compare [OPTIONS] FILEPATH

Options:
  --method TEXT        Which similarity measure to use calculate
                       similarity_score. Currently supports 'frechet_dist'
  --precision INTEGER  Decimal precision to round similarity_score. Default=6.
  --clip TEXT          If True, the similarity_score will be calculated based
                       on the clipped portion of the original geometries
                       within the intersection of each geometry's bounding
                       box. If False, the similarity_score will compare the
                       entirety of the original geometries.
  --clip_max FLOAT     The minimum ratio of length of the clipped geometry to
                       the length of the original geometry, at which to return
                       a non-zero similarity_score.
  --help               Show this message and exit.
```

**Example:**

```
$ bin/geosimilarity compare data/test_compare_files/test_compare1

The similarity score between "LINESTRING (0 0, 1 1, 2 2)" and "LINESTRING (0 0.01, 1 1.01, 2 2.01)" is 0.996471
```
The file ```data/test_compare_files/test_compare1``` contains the following:
```
LINESTRING (0 0, 1 1, 2 2)
LINESTRING (0 0.01, 1 1.01, 2 2.01)
```

## To run "similarity" on two GeoDataFrames

```
$ bin/geosimilarity similarity [filepath1] [filepath2] [--rf=''] [--how='sindex'] [--drop_zeroes=False] [--keep_geom='left'] [--method='frechet_dist'] [--precision=6] [--clip=True] [--clip_max=0.5]
```

```filepath1``` and ```filepath2``` must contain a ```*.shp``` file with its corresponding ```*.cpg```, ```*.dbf```, ```*.prj```, and ```*.shx``` files in the same directory to be read by ```geopandas.read_file(*.shp)```. 

If you want to save the result table to a file, you must provide a filepath to ```--rf``` that ends in ```*.csv``` (saving to ```*.shp``` will come soon, currently shapefiles can only contain one geometry column, whereas the result similarity table contains two geometry columns).

**Use --help to see descriptions of options**

```
$ bin/geosimilarity similarity --help
```

```
$ bin/geosimilarity similarity --help
Usage: main.py similarity [OPTIONS] FILEPATH1 FILEPATH2

Options:
  --rf TEXT            Filepath to store result dataframe.
  --how TEXT           'sindex' to merge GeoDataFrames on spatial index,
                       'cartesian' to merge by cartesian product.
  --drop_zeroes TEXT   If True, rows in the result GeoDataFrame with a
                       similarity_score of 0 will be dropped.
  --keep_geom TEXT     'left' and 'right' to set geometry column in result
                       GeoDataFrame to df1's and df2's original geometry
                       column, respectively.
  --method TEXT        Which similarity measure to use calculate
                       similarity_score. Currently supports 'frechet_dist'
  --precision INTEGER  Decimal precision to round similarity_score. Default=6.
  --clip TEXT          If True, the similarity_score will be calculated based
                       on the clipped portion of the original geometries
                       within the intersection of each geometry's bounding
                       box. If False, the similarity_score will compare the
                       entirety of the original geometries.
  --clip_max FLOAT     The minimum ratio of length of the clipped geometry to
                       the length of the original geometry, at which to return
                       a non-zero similarity_score.
  --help               Show this message and exit.
```

**Example:**

```
$ bin/geosimilarity similarity data/line1/line1.shp data/line1_distance_gradient/line1_distance_gradient.shp --rf='data/result.csv' --how='cartesian' --precision=20 --drop_zeroes=True --clip=False
+--------+-----------+-----------------------------------------------------------+-----------+-----------------------------------------------------------------+--------------------+
|        |   value_x | geometry_x                                                |   value_y | geometry_y                                                      |   similarity_score |
|--------+-----------+-----------------------------------------------------------+-----------+-----------------------------------------------------------------+--------------------|
| (0, 0) |         1 | LINESTRING (-122.3 37.82, -122.31 37.825, -122.32 37.822) |         1 | LINESTRING (-122.3 37.82, -122.31 37.825, -122.32 37.822)       |           1        |
| (0, 1) |         1 | LINESTRING (-122.3 37.82, -122.31 37.825, -122.32 37.822) |         1 | LINESTRING (-122.3 37.8205, -122.3105 37.825, -122.3205 37.822) |           0.977139 |
| (0, 2) |         1 | LINESTRING (-122.3 37.82, -122.31 37.825, -122.32 37.822) |         1 | LINESTRING (-122.3 37.822, -122.31 37.827, -122.319 37.824)     |           0.901746 |
| (0, 3) |         1 | LINESTRING (-122.3 37.82, -122.31 37.825, -122.32 37.822) |         1 | LINESTRING (-122.3 37.824, -122.31 37.829, -122.32 37.826)      |           0.831097 |
| (0, 4) |         1 | LINESTRING (-122.3 37.82, -122.31 37.825, -122.32 37.822) |         1 | LINESTRING (-122.3 37.8285, -122.32 37.8285)                    |           0.612607 |
+--------+-----------+-----------------------------------------------------------+-----------+-----------------------------------------------------------------+--------------------+
Result saved to data/result.csv
```

# Run Tests

```
$ pytest
```

```
$ pytest
================================== test session starts ==================================
platform darwin -- Python 3.6.5, pytest-6.1.0, py-1.9.0, pluggy-0.13.1
rootdir: /Users/audreyku/Desktop/geosimilarity
collected 13 items                                                                                                                                                                                  

tests/test_compare.py .......                                                       [ 53%]
tests/test_linestring_tools.py ...                                                  [ 76%]
tests/test_similarity.py ...                                                        [100%]

=================================== 13 passed in 0.91s ===================================
```

# Sample data files
Some sample data files are provided in ```geosimilarity/data```. ```*.shp``` files are in folders with their corresponding ```*.cpg```, ```*.dbf```, ```*.prj```, and ```*.shx``` files and can be input into the ```similarity method```. The folder ```geosimilarity/data/test_compare_files``` contains text files containing two lines of LineStrings to be input into the ```compare``` method.

See more of the background, ideation, and implementation process in this Notion document:
https://www.notion.so/OSS-Contribution-Geopandas-Overlay-Similar-Geometries-623ac9054c8648b6936ef04793c2899b
