#### Bicycle crash analysis using instance segmentation

##### Introduction

Bicycle usage carries several benefits, from less traffic congestion in cities,
less polution, healthier lifestyle, among others.

However, cyclist are vulnerable road users, which crash rate is in increase
<cite>[Eco24][1]</cite>.

For this reason, research in the field of bicycle crashes during the 15 last
years have gained popularity.

Within the types of bicycle crahes, one that stands out is the Single-actor
bicycle crash, where no other road user is involved.



Understanding the behaviour of bicycle in crash scenarios will enhance research
quality in the field and increase road safety.

To this end, it is necessary to first understand frequent crash configurations
and bicycle crash dynamics.




In the literature we can find several vehicular crash analyses, mainly for cars.

However, for bicycles and motorcycles, these approaches are limited, beginning
with the low 'after crash' traces \cite{}.

In this matter, we define crash stages based on a video datased created from
public domain sources \ref{}.



 

##### Method


Mention somewhere here that we are using instance segmentation.



- Data collection

This research have been based on manually selected videos from public domain
sources.


- Video labelling

In the training phase, videos were annotated using CVAT for instance segmentation
in YOLO format.

Using this approach, we label ellipses for the wheels using front and rear as
the features.

We extract the position of the center of the ellipse along with the axes and
angle.





To train the computer vision algorithm, several bicycle videos of normal riding
and crash scenarios were labeled.

We use the ellipse labelling approach, taking advantage from neural networks
already trained to detect wheels from side view.

Assuming that the majority of the bicycles use wheels of standarised sizes, we
expect that this allows us in the future to use triangulation techniques in
kinematic data extraction.

Additionally, ellipses give information about the orientation to the camera
based on its excentricity.


- Supervised learning for detecting crashes

The first task to try the proposed methodology is to feed the model with
labelled data of crash/ no crash.

From wheel motion in space, neglecting spinning for technical constraints
(image quality), we can detect if the image corresponds or not to a crash.


- Unsupervised (clustering) for classifying crashes and compare with literature.

Using detected crashes and the previously mentioned dataset, we use clustering
techniques to identify different crash configurations.

We expect to link these clusters to the previously developed classification.




##### Results

- This methodology allows us to detect common crashes from side-view perspectives.

With this work, we create a comprehensive bicycle dynamics-oriented base of
technical requirements for crash analysis.

The stages of a bicycle crash are identified: Excitation creates critical
scenario, mechanism and motion are the crash characteristics, while the post
crash is mainly related to human motion and outcome.

With this classification we highlight the necessity of data on bicycle crashes.


- Pitch over crashes are easier to identify

Using the ellipse-based approach, pitch-over crashes present a higher prediction
accuracy.


##### Discussion

- Bicycles are particularly challenging for computer vision tasks
- This is a new approach that have not been done before.
- Combining this with triangulation methods can open the door for kinematics
extraction.
- Limitations: Side view, not longitudinal slip detection, image quality.
- Camera motion

##### Conclusion

This approach seems to be promising for the desired task.

It is necessary to increase dataset size.

Events with large longitudinal and/or vertical motion of the bicycle are more
easy to identify.



#### References

[1]: European Commission (2024) Facts and Figures Cyclists. European Road Safety
Observatory. Brussels, European Commission, Directorate General for Transport.

