Bicycle crash motion using instance segmentation
================================================

Introduction
------------

Bicycle usage carries several benefits, from less traffic congestion and
pollution in cities to healthier lifestyles. However, cyclists are vulnerable
road users, and crash rates are increasing (European Commission 2024). For this
reason, a better understanding of why and how crashes occur is needed. Within
the types of bicycle crashes, single-cyclist crashes stand out because its share
ranges from 50% to 85% of bicycle-related hospital admissions
(Utriainen et al. 2023).


For example, a common crash configuration is known as 'pitch-over'. This occurs
when, due to excessive longitudinal load transfer, the rear wheel lifts from the
ground and the bicycle rotates around the contact point of the front wheel, see
Figure 1 (Gildea et al. 2021).


The lack of motion data on these events is commonly discussed in the literature
(Utriainen 2020). However, no solutions that increase the data exist, and
recreating crashes leads to dangerous situations even in laboratory-controlled
setups. For this reason, we propose to use video instance segmentation to gather
bicycle motion data from monocular videos. Specifically, instance segmentation
is the task of detecting an object and demarcating its shape simultaneously on
the image (Hafiz, A.M., Bhat, G.M. 2020). 


Although there are examples of bicycle crash in the literature, its analysis
using computer vision methods was focused on the rider fall outcome and not on
the bicycle's particular motion (Gildea et al. 2024). Therefore, our aim was
to gather bicycle crash motion data from monocular videos and extract the bicycle's motion. To this end, we
created a dataset of single-cyclist crashes from web sources. From these videos,
we track the motion of the bicycle by identifying and tracking the position of
the wheels.

Methods
-------

To create a database of single-cyclist crash videos, we manually selected publicly 
available videos from online platforms, such as YouTube. Selected videos contain bicycle
crashes where no other road user is involved, or if there is another user, its
participation effect is assumed as negligible, i.e. the exerted
force is uncontrolled and it does not depend on the source. The dataset
consists of 100 videos with an average duration of three seconds, along with their time
stamp on the source.


The dataset was annotated for instance segmentation with ellipse shapes for
wheels, labelling them with 'front' and 'rear' as features. These annotations
give the boundary points of the ellipses, from which we obtain the position of
wheel centres (in pixels) and their orientation by estimating the rotation angle
with respect to the vertical axis. In addition, we calculate the ratio between
the minor and major axes of the ellipses, from which it is possible to estimate
the viewing angle. Lastly, we calculate the x and y distances in pixels between
the centres of both ellipses.


Results
-------

Three annotated video frames are shown along with the coordinate system and a
schematic representation of the crash motion in Figure 1, showing successful tracking
of the front and rear wheels. Then, extracted data from this video is shown in
Figure 2. In the top row, we show the x and y positions of the wheels' centres with respect to the frame numbers,
along with the ratio between the major and the minor axes of the ellipses. In
the bottom row, we plot the distance between wheel centres in both axes, along
with the angle with respect to the vertical axis of the ellipses.


We observe that after frame 100, the rear wheel moves forward over the front
wheel. Similarly, between frames 85 and 105, there is a major increase in the
vertical position of the rear wheel. Taking into account the average distance in
the $y$ axis between both wheel centres, a peak is observed during the crash 
motion, which is equivalent to 283% of the average distance.


Discussion
----------

In this research we addressed the problems of the lack of real-world
single-cyclist crash motion data and its analysis using computer vision techniques.
Using instance segmentation, we were able to track the position of the wheels of
the bicycle in the image and analyse its crash motion.


From preliminary results, we observe that sudden variations in the distance
between wheel centres allows to identify crashes with large vertical rotations
of the bicycle, such as pitch-over crashes. Alternatively, some limitations of this approach are low video quality, undefined camera
motion, and inconsistent frame rate.


Summarising, the presented methodology allows to gathering useful data from
real-world scenarios for its analysis. By integrating different techniques into
the pipeline used in this work, results can be enhanced, taking into account the 
mentioned limitations. This work continues in development to apply classification
methods to the gathered data.



Conclusion
----------

In this work we created a video dataset of single-cyclist crashes. Using
computer vision techniques, we extracted 2-dimensional motion data of the
wheels in different crash scenarios. We conclude that side-recorded videos 
provide greater quality data using this approach. Additionally, crash
configurations where large vertical motions occur are easier to identify.
Further work will be to assess near-miss situations to compare and apply machine
learning algorithms to the data to cluster the types of crashes.



References
----------

European Commission (2024) Facts and Figures Cyclists. European Road Safety Observatory. Brussels, European Commission, Directorate General for Transport.

Gildea, K., Hall, D., & Simms, C. (2021). Configurations of underreported cyclist-motorised vehicle and single cyclist collisions: Analysis of a self-reported survey. Accident Analysis & Prevention, 159, 106264.

Gildea, K., Hall, D., Cherry, C. R., & Simms, C. (2024). Forward dynamics computational modelling of a cyclist fall with the inclusion of protective response using deep learning-based human pose estimation. Journal of Biomechanics, 163, 111959.

Hafiz, A.M., Bhat, G.M. (2020) A survey on instance segmentation: state of the art. Int J Multimed Info Retr 9, 171–189.

Utriainen, R. (2020). Characteristics of Commuters’ Single-Bicycle Crashes in Insurance Data. Safety 2020, 6(1), 13.

Utriainen, R., O’Hern, S., & Pöllänen, M. (2023) Review on single-bicycle crashes in the recent scientific literature, Transport Reviews, 43:2, 159-177.
