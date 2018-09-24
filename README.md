# depthCamerasRemoteControl
## Overview
This project is a full stack web-based application which is used for the system administrators or engineers to
remotely calibrate a set of depth cameras.
Communication between camera control system and this remote calibration system is done by using GRPC and MQTT
protocol. The models presentation and manipulation is done by using three.js. The framework for contructing the
web application is Django and the project is encapsulated in a docker container.
To run the web application, use command:
sudo docker-compose run
under the directory with docker-compose.yml file.
Note that the system needs to work collaborately with a camera control system to function properly.

## Workflow
When the service starts, back-end server will repeatedly try to receive heart-beat messages sent by camera control
system which contains the MAC address of active device (the message will be sent under a specific topic). The user
can then select which device to adjust based on the MAC address.
The user will have options including: train main/sub background model, check training process, upload main/sub
background model, upload foreground model, present model and start calibration and restart depth camera.
When models are trained and uploaded, user can start camera calibration.
The calibration is done by comparing different set of main/sub background models and the foreground model, by
manually adjust models (vertically/horizontally move, rotate, etc.) to desired positions, user can obatin the
difference in parameters requried to define a surface (e.g. a, b and d in ax+by+cz+d=0) and hence use the difference
to adjust camera angles and calibrate them for more accuracy.
The depth camera control system will send the captured 3D point cloud data to the back-end server, and then after
parsing and decoding, the data will be presented by front-end service, i.e. 3D views that depth cameras captured
will be shown on the webpage. Users can use keyboard and mouse to manipulate different set of models.
When calibration is done, the data of models after adjustment will be sent back to camera control system and will
be used to calculate the difference in surface parameters.

