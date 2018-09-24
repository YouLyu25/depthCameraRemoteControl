from django.urls import path, include
from django.contrib import admin
from . import views

admin.autodiscover()

urlpatterns = [
    path('showActiveDevice', views.showActiveDevice, name='showActiveDevice'),
    path('directToControlInterface', views.directToControlInterface, name='directToControlInterface'),
    path('requestForRemoteControl', views.requestForRemoteControl, name='requestForRemoteControl'),
    path('trainMainBGModel', views.trainMainBGModel, name='trainMainBGModel'),
    path('trainSubBGModel', views.trainSubBGModel, name='trainSubBGModel'),
    path('uploadMainBGModel', views.uploadMainBGModel, name='uploadMainBGModel'),
    path('uploadSubBGModel', views.uploadSubBGModel, name='uploadSubBGModel'),
    path('restartDepthCamera', views.restartDepthCamera, name='restartDepthCamera'),
    path('finishModelsCalibration', views.finishModelsCalibration, name='finishModelsCalibration'),
    path('modifyRotationMatrix', views.modifyRotationMatrix, name='modifyRotationMatrix'),
    path('finishFloorCalibration', views.finishFloorCalibration, name='finishFloorCalibration'),
    path('directToModelCalibration', views.directToModelCalibration, name='directToModelCalibration'),
    path('downloadModels', views.downloadModels, name='downloadModels'),
    path('loadModels', views.loadModels, name='loadModels'),
    path('uploadFrontGround', views.uploadFrontGround, name='uploadFrontGround'),
    path('checkActiveDevice', views.checkActiveDevice, name='checkActiveDevice'),
    path('checkModelsTrainingProgress', views.checkModelsTrainingProgress, name='checkModelsTrainingProgress'),
    path('checkDataStatus', views.checkDataStatus, name='checkDataStatus'),
    path('checkFGDataStatus', views.checkFGDataStatus, name='checkFGDataStatus'),
    path('checkDeviceStatus', views.checkDeviceStatus, name='checkDeviceStatus'),
    path('checkCalibrationStatus', views.checkCalibrationStatus, name='checkCalibrationStatus'),
]
