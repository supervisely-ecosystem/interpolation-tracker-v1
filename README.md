<div align="center" markdown> 
<img src="xxx" />

# Interpolation tracker
  
<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#Polygons-interpolation-settings">Polygons interpolation settings</a> 
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/interpolation_tracker_v1)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/interpolation_tracker_v1)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/interpolation_tracker_v1)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/interpolation_tracker_v1)](https://supervise.ly)

</div>

# Overview 

This tracker uses linear (pointwise) interpolation between figures on various frames to track points, polygons, and rectangles.

# How To Run

1. Start the application from Ecosystem
 
<br>

2. Select the polygon interpolation algorithm: Greedily or Uniform. See how they differ <a href="#Polygons-interpolation-settings">here</a>

<img src="xxx" />

3. 

4. 

5.

# Polygons interpolation settings

One of the algorithms that will be used to interpolate between forms with various numbers of vertices need to be chosen when interpolating polygons.
There are 2 options

## Greedily (default)

| First frame polygon                                                                                                   | Created polygon                                                                                                      | n-th frame polygon                |
| --------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| ![uniform_end](https://user-images.githubusercontent.com/87002239/231024683-360ec789-2764-49c9-90c6-014dd17d7dd2.png) | ![greedy_mid](https://user-images.githubusercontent.com/87002239/231024687-b32de7b8-2879-42d6-aa7c-ec05f3a6a905.png) |![greedy_end](https://user-images.githubusercontent.com/87002239/231024688-89c78047-0c88-488c-be88-6eca06a9c094.png) |

Each new polygon will include no more points than the largest of the start or end frames if the number of points for a polygon on the start and end frames varies.
Small polygons respond well to the method, but because there aren't many points, polygons may begin to rotate.

## Uniform

| First frame polygon                                                                                                     | Created polygon                                                                                                       | n-th frame polygon |
| ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------ |
| ![uniform_start](https://user-images.githubusercontent.com/87002239/231024690-dd29b0e4-81f7-4b61-9e13-0525ad61e8de.png) | ![uniform_mid](https://user-images.githubusercontent.com/87002239/231024691-b9048f36-ec11-48c1-961c-97201bc3e44c.png) |![uniform_end](https://user-images.githubusercontent.com/87002239/231024683-360ec789-2764-49c9-90c6-014dd17d7dd2.png)|


The total number of points on the start and end polygons increases until it reaches the least common multiple of those points.
On the sides, new points are distributed uniformly. Some points can be automatically eliminated after interpolation.