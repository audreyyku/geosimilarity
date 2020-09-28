import math
import similaritymeasures as sm

from linestring_tools import line_to_coords
from shapely.geometry import Polygon

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
        clipped2 = line2.intersection(min_box)

        # Line does not intersect minimum bounding box
        if (clipped1.is_empty or clipped2.is_empty):
            return 0

        # In this case, the resulting clipped lines do not accurately
        # represent the similarity between the original lines
        if (clipped1.length < line1.length*clip_max
                or clipped2.length < line2.length*clip_max):
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
