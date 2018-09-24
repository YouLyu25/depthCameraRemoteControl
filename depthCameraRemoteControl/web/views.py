# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import struct
import urllib
import grpc
import resource_pb2
import resource_pb2_grpc
import time

# global variables
TEST = True
mqttServer = "mqtt.demo.meetwhale.com"
mqttPort = 1883
mqttUsername = "whale_smart"
mqttPassword = "Buzhongyao"
grpcChannel = "106.15.189.129:3022"
client = mqtt.Client()
heartBeatTopic = "remote-control/heart-beat"
topicPrefix = "remote-control/"
mainBGDataReady = {}
subBGDataReady = {}
FGDataReady = {}
FGURL = {}
mainFGDataRaw = {}
subFGDataRaw = {}
FGOriginRaw = {}
# mainBGDataURL = "http://whale-face.oss-cn-shanghai.aliyuncs.com/model//0u2vtkx3xoy7sokm.bin"
# subBGDataURL = "http://whale-face.oss-cn-shanghai.aliyuncs.com/model//q8tbbgvt238oe7z1.bin"
mainBGDataURL = {}
subBGDataURL = {}
modelsDownloaded = {}
floorDownloaded = {}
activeInterval = 600000000  # seconds
activeDevice = {}
modelsTrainingProgress = {}
modelsTrainingUpdate = {}


# function called when mqtt client successfully connected to the broker
def on_connect(client, userdata, flags, rc):
    print("Connection returned result: " + str(rc))
    # subscribe specific topic and send MQTT message to let camera train main background model
    print("subscribe: " + heartBeatTopic)
    client.subscribe(heartBeatTopic, qos=1)
    for device, timeStamp in activeDevice.items():
        client.subscribe(topicPrefix + device)
        print("subscribe: " + topicPrefix + device)


# function called when mqtt client received a message
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        infoDict = {}
        msgInfo = payload.split(",")
        for element in msgInfo:
            info = element.split(":")[0]
            infoDict[info] = element.split(":")[1]

        if infoDict["type"] == "response":
            deviceMAC = msg.topic.split("/")[1]
            if infoDict["status"] == "trainedMainBGModel":
                pass
            elif infoDict["status"] == "trainedSubBGModel":
                pass
            if infoDict["status"] == "uploadedMainBGModel":
                # upload main background model download url
                global mainBGDataReady
                mainBGDataReady[deviceMAC] = True
                global mainBGDataURL
                mainBGDataURL[deviceMAC] = "http://" + infoDict["url"]

            elif infoDict["status"] == "uploadedSubBGModel":
                # upload sub background model download url
                global subBGDataReady
                subBGDataReady[deviceMAC] = True
                global subBGDataURL
                subBGDataURL[deviceMAC] = "http://" + infoDict["url"]

            elif infoDict["status"] == "trainingBGModel":
                global modelsTrainingProgress
                global modelsTrainingUpdate
                modelsTrainingProgress[deviceMAC] = infoDict["message"]
                modelsTrainingUpdate[deviceMAC] = True

            elif infoDict["status"] == "downloadedRotated3DCloudData":
                global modelsDownloaded
                modelsDownloaded[deviceMAC] = True

            elif infoDict["status"] == "downloadedFloorParameter":
                global floorDownloaded
                floorDownloaded[deviceMAC] = True

            elif infoDict["status"] == "uploadedFrontGround":
                print("test " + payload)
                global FGURL
                FGURL[deviceMAC] = infoDict["url"]
                # TODO: check the format of mqtt message
                global FGDataReady
                FGDataReady[deviceMAC] = True

            elif infoDict["status"] == "restartedDepthCamera":
                pass

        elif infoDict["type"] == "heartBeat":
            global activeDevice
            # update device checking time
            activeDevice[infoDict["MAC"]] = time.time()

    except Exception as error:
        print("exception caught: " + str(error))


# function called when mqtt client published a message
def on_publish(client, userdata, mid):
    print("\nsuccessfully published\n")


# function called when mqtt client successfully subscribed to a specific topic
def on_subscribe(client, userdata, mid, granted_qos):
    print("\nsuccessfully subscribed\n")


# make connection to the mqtt broker
def makeMqttConnection(mqttServer, mqttPort, client):
    print("\nmaking mqtt connection...\n")
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    try:
        client.username_pw_set(username=mqttUsername, password=mqttPassword)
        client.connect(mqttServer, mqttPort, 6000)
        client.loop_start()
        return 0
    except:
        return -1


# return main interface of web and show active device
def showActiveDevice(request):
    if makeMqttConnection(mqttServer, mqttPort, client) == -1:
        return HttpResponse("cannot connect to the MQTT broker")
    return render(request, "mainInterface.html")


# request remote control to a certain device
def requestForRemoteControl(request):
    if request.POST.get("op") == "request for remote control":
        deviceMAC = request.POST.get("deviceMAC")
        topic = topicPrefix + deviceMAC
        global mainBGDataReady
        global subBGDataReady
        global modelsDownloaded
        global floorDownloaded
        global modelsTrainingProgress
        global modelsTrainingUpdate
        # register device and init its info
        mainBGDataReady[deviceMAC] = False
        subBGDataReady[deviceMAC] = False
        FGDataReady[deviceMAC] = False
        modelsDownloaded[deviceMAC] = False
        floorDownloaded[deviceMAC] = False
        modelsTrainingProgress[deviceMAC] = "training..."
        modelsTrainingUpdate[deviceMAC] = False
        print("\ncontrolling device: " + deviceMAC + "\n")
        # subscribe mqtt message topic that corresponds to a specific device
        client.subscribe(topic)
        return HttpResponse("success")
    return HttpResponseRedirect("showActiveDevice")


# return device control interface
def directToControlInterface(request):
    return render(request, "remoteControl.html")


# publish mqtt message to train main background model
def trainMainBGModel(request):
    if request.POST.get("op") == "train main background model":
        topic = topicPrefix + request.POST.get("deviceMAC")[1:]
        client.publish(topic=topic, payload="type:control,command:trainMainBGModel")
        return HttpResponse("mqtt message train main background model sent")
    return HttpResponseRedirect("showActiveDevice")


# publish mqtt message to train sub background model
def trainSubBGModel(request):
    if request.POST.get("op") == "train sub background model":
        topic = "remote-control/" + request.POST.get("deviceMAC")[1:]
        client.publish(topic=topic, payload="type:control,command:trainSubBGModel")
        return HttpResponse("mqtt message train sub background model sent")
    return HttpResponseRedirect("showActiveDevice")


def uploadMainBGModel(request):
    if request.POST.get("op") == "upload main background model":
        topic = "remote-control/" + request.POST.get("deviceMAC")[1:]
        client.publish(topic=topic, payload="type:control,command:uploadMainBGModel")
        return HttpResponse("mqtt message upload main background model sent")
    return HttpResponseRedirect("showActiveDevice")


def uploadSubBGModel(request):
    if request.POST.get("op") == "upload sub background model":
        topic = "remote-control/" + request.POST.get("deviceMAC")[1:]
        client.publish(topic=topic, payload="type:control,command:uploadSubBGModel")
        return HttpResponse("mqtt message upload sub background model sent")
    return HttpResponseRedirect("showActiveDevice")


def checkModelsTrainingProgress(request):
    if request.POST.get("op") == "check models training progress":
        deviceMAC = request.POST.get("deviceMAC")[1:]
        global modelsTrainingUpdate
        if modelsTrainingUpdate[deviceMAC]:
            modelsTrainingUpdate[deviceMAC] = False
            return HttpResponse(modelsTrainingProgress[deviceMAC])
        return HttpResponse("no update")
    return HttpResponseRedirect("showActiveDevice")


# publish mqtt message to let camera return to operating status
def restartDepthCamera(request):
    if request.POST.get("op") == "restart depth camera":
        topic = "remote-control/" + request.POST.get("deviceMAC")[1:]
        print("restart: " + topic)
        client.publish(topic=topic, payload="type:control,command:restartDepthCamera")
        return HttpResponse("mqtt message restart depth camera sent")
    return HttpResponseRedirect("showActiveDevice")


def uploadFrontGround(request):
    if request.POST.get("op") == "upload front ground":
        topic = "remote-control/" + request.POST.get("deviceMAC")[1:]
        id = request.POST.get("id")
        client.publish(topic=topic, payload="type:control,command:uploadFrontGround,messageID:" + str(id))
        return HttpResponse("mqtt message upload front ground sent:" + str(id))
    return HttpResponseRedirect("showActiveDevice")


def showFrontGround(request):
    return


# finish the calibration of two models, upload calibrated data
def finishModelsCalibration(request):
    if request.POST.get("op") == "finish models calibration":
        topic = "remote-control/" + request.POST.get("deviceMAC")[1:]
        result = request.POST.get("result")
        resultFloatArray = json.loads(result)
        # upload rotated result to remote server using gRPC
        rotated3DCloudData = struct.pack("f", resultFloatArray[0])
        for i in range(1, len(resultFloatArray)):
            rotated3DCloudData += struct.pack("f", resultFloatArray[i])
        # upload rotated cloud data onto server via gRPC call
        uploadUrl = uploadRotated3DCloudData(grpcChannel, rotated3DCloudData)
        client.publish(topic=topic, payload="type:control,command:downloadRotated3DCloudData,url:" + uploadUrl)
        return HttpResponse("download rotated 3D cloud data message sent")
    return HttpResponseRedirect("showActiveDevice")


def modifyRotationMatrix(request):
    if request.POST.get("op") == "modify rotation matrix":
        deviceMAC = request.POST.get("deviceMAC")[1:]
        topic = "remote-control/" + deviceMAC
        rotatedMatrix = request.POST.get("rotatedMatrix")
        print(rotatedMatrix)
        resultFloatArray = json.loads(rotatedMatrix)
        print(resultFloatArray[0:300])
        result = ""
        for element in resultFloatArray[0:300]:
            result += str(element) + "/"
        result = result[:-1]
        client.publish(topic=topic, payload="type:control,command:modifyRotationMatrix,"
                                            "rotatedSubFG3DCloud:" + result +
                                            ",originSubFG3DCloud:" + FGOriginRaw[deviceMAC])
        return HttpResponse("modify rotation matrix message sent")
    return HttpResponseRedirect("showActiveDevice")


# finish the calibration of floor
def finishFloorCalibration(request):
    if request.POST.get("op") == "finish floor calibration":
        topic = "remote-control/" + request.POST.get("deviceMAC")[1:]
        paramA = request.POST.get("paramA")
        paramB = request.POST.get("paramB")
        paramC = request.POST.get("paramC")
        paramD = request.POST.get("paramD")

        payload = "paramA:" + paramA + ",paramB:" + paramB + ",paramC:" + paramC + ",paramD:" + paramD
        client.publish(topic=topic, payload="type:control,command:downloadFloorParameter," + payload)
        return HttpResponse("download floor parameter message sent")
    return HttpResponseRedirect("showActiveDevice")


# upload rotated 3D point cloud data to the file server using gRPC
def uploadRotated3DCloudData(grpcChannel, data):
    channel = grpc.insecure_channel(grpcChannel)
    stub = resource_pb2_grpc.ResourceServiceStub(channel)
    response = stub.UploadModel(resource_pb2.UploadModelReq(file=data))
    print("client received: " + response.filename + ", " + response.url)
    return response.url


# redirect to model calibration page
def directToModelCalibration(request):
    return render(request, "modelCalibration.html")


# check if models are downloaded successfully
def downloadModels(request):
    global f
    if request.POST.get("role") == "main":
        deviceMAC = request.POST.get("deviceMAC")[1:]
        try:
            f = urllib.request.urlopen(mainBGDataURL[deviceMAC])
        except Exception as error:
            print("exception caught: " + str(error))
            return HttpResponse("fail to download main model data")
        finally:
            f.close()
        return HttpResponse("main model data downloaded")
    elif request.POST.get("role") == "sub":
        deviceMAC = request.POST.get("deviceMAC")[1:]
        try:
            f = urllib.request.urlopen(subBGDataURL[deviceMAC])
        except Exception as error:
            print("exception caught: " + str(error))
            return HttpResponse("fail to download sub model data")
        finally:
            f.close()
        return HttpResponse("sub model data downloaded")
    else:
        return HttpResponseRedirect("showActiveDevice")


# load and display downloaded models to the web page
def loadModels(request):
    dataFloatArray = []
    if request.POST.get("role") == "main":
        deviceMAC = request.POST.get("deviceMAC")[1:]
        # if request main background data
        f = urllib.request.urlopen(mainBGDataURL[deviceMAC])
        try:
            while True:
                # read 4 bytes at a time as data is 32-bit float
                dataBytes = f.read(4)
                if len(dataBytes) == 0:
                    break
                dataFloatArray.append(struct.unpack("f", dataBytes))
        finally:
            f.close()
    elif request.POST.get("role") == "sub":
        deviceMAC = request.POST.get("deviceMAC")[1:]
        # if request sub background data
        f = urllib.request.urlopen(subBGDataURL[deviceMAC])
        try:
            while True:
                # read 4 bytes at a time as data is 32-bit float
                dataBytes = f.read(4)
                if len(dataBytes) == 0:
                    break
                dataFloatArray.append(struct.unpack("f", dataBytes))
        finally:
            f.close()
    else:
        return HttpResponseRedirect("showActiveDevice")
    return HttpResponse(dataFloatArray)


# update device that is currently active, return a string of active device list
def checkActiveDevice(request):
    global activeDevice
    activeList = ""
    removeList = []
    if request.POST.get("op") == "check active device":
        for device, timeStamp in activeDevice.items():
            print(time.time() - activeDevice[device])
            if time.time() - activeDevice[device] > activeInterval:
                # device is no longer active, remove from the active list
                print("check: " + str(device))
                removeList.append(device)
            else:
                activeList += device + ","
        activeList = activeList[:-1]
        for device in removeList:
            print(device)
            activeDevice.pop(device)
        return HttpResponse(activeList)
    return HttpResponseRedirect("showActiveDevice")


# front-end will send Http request to check if both main and sub background model are ready
def checkDataStatus(request):
    if request.POST.get("op") == "check data status":
        deviceMAC = request.POST.get("deviceMAC")[1:]
        global mainBGDataReady
        global subBGDataReady
        if mainBGDataReady[deviceMAC] and subBGDataReady[deviceMAC]:
            mainBGDataReady[deviceMAC] = False
            subBGDataReady[deviceMAC] = False
            return HttpResponse("data is ready")
        elif mainBGDataReady[deviceMAC]:
            return HttpResponse("main model data is uploaded")
        elif subBGDataReady[deviceMAC]:
            return HttpResponse("sub model data is uploaded")
        return HttpResponse("data is not ready")
    return HttpResponseRedirect("showActiveDevice")


# check if device is currently active
def checkDeviceStatus(request):
    if request.POST.get("op") == "check device status":
        deviceMAC = request.POST.get("deviceMAC")[1:]
        global activeDevice
        if time.time() - activeDevice[deviceMAC] > activeInterval:
            # device is no longer active, remove from the active list
            activeDevice.pop(deviceMAC)
            return HttpResponse("down")
        return HttpResponse("active")
    return HttpResponseRedirect("showActiveDevice")


FGCount = 0


def checkFGDataStatus(request):
    if request.POST.get("op") == "check FG data status":
        deviceMAC = request.POST.get("deviceMAC")[1:]
        global FGDataReady, f
        if FGDataReady[deviceMAC]:
            FGDataReady[deviceMAC] = False
            # TODO: download FG data using URL provided
            global FGCount
            if TEST and FGCount == 0:
                print("checkFGDataStatus")
                f = open("static/FG3DCloudMessage_0.txt")
                FGCount = 1
            elif TEST and FGCount == 1:
                f = open("static/FG3DCloudMessage_1.txt")
                FGCount = 2
            elif TEST and FGCount == 2:
                f = open("static/FG3DCloudMessage_2.txt")
                FGCount = 0
            elif not TEST:
                f = urllib.request.urlopen("http://" + FGURL[deviceMAC])
            try:
                infoDict = {}
                for line in f:
                    if TEST:
                        dataStr = str(line)
                    else:
                        dataStr = str(line)[2:-1]
                    fileInfo = dataStr.split(",")
                    for element in fileInfo:
                        info = element.split(":")[0]
                        infoDict[info] = element.split(":")[1]
                        print("key: " + info + ", value: " + infoDict[info])
                global FGOriginRaw
                mainFGDataRaw = infoDict["mainFG3DCloud"]
                subFGDataRaw = infoDict["subFG3DCloud"]
                FGOriginRaw[deviceMAC] = infoDict["originSubFG3DCloud"]
                id = infoDict["messageID"]
            finally:
                f.close()
            return HttpResponse(mainFGDataRaw + "#" + subFGDataRaw + "#" + id + "#" + FGOriginRaw[deviceMAC])
        return HttpResponse("FG data not ready")
    return HttpResponseRedirect("showActiveDevice")


# check if calibration is finished
def checkCalibrationStatus(request):
    if request.POST.get("op") == "check calibration status":
        deviceMAC = request.POST.get("deviceMAC")[1:]
        global modelsDownloaded
        global floorDownloaded
        if modelsDownloaded[deviceMAC] and floorDownloaded[deviceMAC]:
            modelsDownloaded[deviceMAC] = False
            floorDownloaded[deviceMAC] = False
            return HttpResponse("downloaded")
        elif modelsDownloaded[deviceMAC]:
            return HttpResponse("models downloaded")
        elif floorDownloaded[deviceMAC]:
            return HttpResponse("floor downloaded")
        return HttpResponse("downloading...")
    return HttpResponseRedirect("showActiveDevice")
