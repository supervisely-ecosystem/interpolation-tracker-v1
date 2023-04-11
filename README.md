# Interpolation tracker (v1 app)

This tracker uses linear (pointwise) interpolation between figures on various frames to track points, polygons, and rectangles.

## Polygons interpolation settings

One of the algorithms that will be used to interpolate between forms with various numbers of vertices need to be chosen when interpolating polygons.
There are 2 options

### Uniform

| First frame polygon                  | Created polygon                    | n-th frame polygon                 |
| ------------------------------------ | ---------------------------------- | ---------------------------------- |
| ![](/src/examples/uniform_start.png) | ![](/src/examples/uniform_mid.png) | ![](/src/examples/uniform_end.png) |


The total number of points on the start and end polygons increases until it reaches the least common multiple of those points.
On the sides, new points are distributed uniformly. Some points can be automatically eliminated after interpolation.


## Greedily

| First frame polygon                | Created polygon                   | n-th frame polygon                |
| ---------------------------------- | --------------------------------- | --------------------------------- |
| ![](/src/examples/uniform_end.png) | ![](/src/examples/greedy_mid.png) | ![](/src/examples/greedy_end.png) |

Each new polygon will include no more points than the largest of the start or end frames if the number of points for a polygon on the start and end frames varies.
Small polygons respond well to the method, but because there aren't many points, polygons may begin to rotate.