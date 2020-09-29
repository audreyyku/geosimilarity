# Geosimilarity

Computes similarity between geometries of two GeoDataFrames

# Problem:
- Slight differences in geometries can make it difficult to perform certain operations such as geopandas.overlay(...)
- This is especially the case for LineStrings

# Real world context:
- Given two GeoDataFrames from two separate data sources, one representing the streets of city and one representing the bus routes of a city
- Slight misalignments can make it so the LineStrings representing the same streets in the physical world are deemed different geometries and thus different streets
- How can we easily identify which street LineStrings are very similar (and are likely to represent the same street in the physical world)?

# Implementation
- Combines two GeoDataFrames and computes the similarity_score between the geometries of each GeoDataFrame
- The similarity_score, which ranges from 0.0 (completely dissimilar) to 1.0 (completely similar), is determined based on the Frechet distance using the formula e^(-frechet/line.length)

# Set up
```
$ git clone https://github.com/ukyerdua/geosimilarity.git
$ cd geosimilarity
$ pip3 install -r requirements.txt
$ export PYTHONPATH="$PWD/geosimilarity"
```
If you do not set the PYTHONPATH to geosimilarity/geosimilarity/, then the test files will not be able to read the functions to be tested in geosimilarity/geosimilarity/*.py

# Run CLI
## Use --help to see functions (commands) available:
```$ bin/geosimilarity -- help```

## To run "compare" on two LineStrings
```$ bin/geosimilarity compare [filename] [--method='frechet_dist'] [--precision=6] [--clip=True] [--clip_max=0.5]```

**Use --help to see descriptions of options**
```$ bin/geosimilarity compare --help```

**Example:**
```$ bin/geosimilarity compare data/test_compare_files/test_compare1```

## To run "similarity" on two GeoDataFrames
```$ bin/geosimilarity similarity [filename1] [filename2] [--rf=''] [--how='sindex'] [--drop_zeroes=False] [--keep_geom='left'] [--method='frechet_dist'] [--precision=6] [--clip=True] [--clip_max=0.5]```

**Use --help to see descriptions of options**
```$ bin/geosimilarity similarity --help```

**Example:**
```$ bin/geosimilarity similarity data/line1/line1.shp data/line1_distance_gradient/line1_distance_gradient.shp --how='cartesian' --precision=20 --drop_zeroes=True --clip=False```

# Run Tests
```$ pytest```

See more of the background, ideation, and implementation process in this Notion document:
https://www.notion.so/OSS-Contribution-Geopandas-Overlay-Similar-Geometries-623ac9054c8648b6936ef04793c2899b
