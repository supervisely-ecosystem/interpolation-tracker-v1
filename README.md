<div align="center" markdown> 
<img src="https://user-images.githubusercontent.com/115161827/231768642-879cd495-903e-4ef2-a3de-b45a91a6f968.jpg" />

# Interpolation tracker
  
<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#Track-Examples">Track Examples</a> •
  <a href="#Polygons-interpolation-settings">Polygons interpolation settings</a> 
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervisely.com/apps/supervisely-ecosystem/interpolation-tracker-v1)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervisely.com/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/interpolation-tracker-v1)
[![views](https://app.supervisely.com/img/badges/views/supervisely-ecosystem/interpolation-tracker-v1)](https://supervisely.com)
[![runs](https://app.supervisely.com/img/badges/runs/supervisely-ecosystem/interpolation-tracker-v1)](https://supervisely.com)

</div>

# Overview 

This app is used to track the movement and position of objects within a video. This application uses linear (pointwise) interpolation to estimate the position of an object between two known data points in order to accurately track its movement over time. The Interpolation tracker works with points, rectangles, and polygons (polygon has two interpolation algorithms to choose from).

# How To Run

1. Start the application from Ecosystem

2. Select the <a href="#Polygons-interpolation-settings">polygons interpolation settings</a> and click `Run` button
![screenshot-dev-supervise-ly-ecosystem-apps-interpolation_tracker_v1-1681394922857](https://user-images.githubusercontent.com/115161827/231813349-16eefdf2-fe28-4ab6-9efc-86e7a9f0024f.png)


4. Run the video labeling interface on the project you want to work with

3. Create classes with Polygon, Point, or Rectangle shapes and then draw figures on the several frames. There can only be one figure per object (class) in a frame

4. Choose the start frame (or range of frames via the Select tool), in track settings select running Interpolation Tracker app, direction, and number of frames

5. Click `Track` button. When a figure on the starting frame is selected, tracking begins for that figure. If no figures are selected, tracking starts for all of the figures on the frame. Be aware that tracking will not work if some class has only a figure in the start frame and none in the tracking direction (see example below)
![gif-objects-interpolation](https://user-images.githubusercontent.com/115161827/231813506-8f7255dd-9cbd-40d5-8337-477d0f4d816d.gif)

# Track Examples

<div align="center">

<img src="https://user-images.githubusercontent.com/87002239/231757938-730b1deb-5887-47d7-a299-616411ffefa3.png" />

</div>

Frames #18, #25, #30 contains figures of 3 different objects.

| Objects   | Frames with figure | Frame range    | Track result                                                                  |
| --------- | ------------------ | -------------- | ----------------------------------------------------------------------------- |
| Object #1 | 18, 25, 30         | 18-27, forward | New figures will appear at frames 18-27                                       |
| Object #2 | 18, 25             | 18-27, forward | New figures will appear at frames 18-25                                       |
| Object #3 | 18                 | 18-27, forward | Tracking will fail because object #3 lacks sufficient data for interpolation. |


# Polygons interpolation settings

One of the algorithms that will be used to interpolate between forms with various numbers of vertices need to be chosen when interpolating polygons.
There are 2 options

## Greedily (default)

| First frame polygon                                                                                                   | Created polygon                                                                                                      | n-th frame polygon                |
| --------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| ![g_first](https://user-images.githubusercontent.com/115161827/231856880-d52eb375-4f1f-45f6-9f8b-8d334efb2b7d.png)| ![g_middle](https://user-images.githubusercontent.com/115161827/231856930-18d2d3f0-7252-40e8-bfa8-0541338edbc3.png)|![g_last](https://user-images.githubusercontent.com/115161827/231856988-311de766-e1d1-482b-acd7-51781c84c3ed.png)



Each new polygon will include no more points than the largest of the start or end frames if the number of points for a polygon on the start and end frames varies.
Small polygons respond well to the method, but because there aren't many points, polygons may begin to rotate.

## Uniform

| First frame polygon                                                                                                     | Created polygon                                                                                                       | n-th frame polygon |
| ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------ |
|![u_first](https://user-images.githubusercontent.com/115161827/231857037-481affe0-b844-4b22-96a0-437479e6e318.png)| ![u_middle](https://user-images.githubusercontent.com/115161827/231857099-0d4bbcaf-9b96-4312-8cb6-0e94da1fbf8a.png)| ![u_last](https://user-images.githubusercontent.com/115161827/231857156-36911631-a786-47e0-bbcc-58b1a437e9b9.png)




The total number of points on the start and end polygons increases until it reaches the least common multiple of those points.
On the sides, new points are distributed uniformly. Some points can be automatically eliminated after interpolation.
