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

See more of the background, ideation, and implementation process in this Notion document:
https://www.notion.so/OSS-Contribution-Geopandas-Overlay-Similar-Geometries-623ac9054c8648b6936ef04793c2899b
