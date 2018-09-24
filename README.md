# depthCamerasRemoteControl
This project is a full stack web-based application which is used for the system administrators or engineers to
remotely calibrate a set of depth cameras.
When the service starts, back-end server will repeatedly receive heart-beat messages sent by camera control system
which contains the MAC address of active device.
The depth camera control system will send the captured 3D point cloud data to the back-end server, and then after
parsing and decoding the data will be presented by front-end service, i.e. 3D views that depth cameras captured
will be shown on the webpage.
The communication between camera control system and this remote calibration system is done by using GRPC and MQTT
protocol. The framework for contructing the web application is Django.
