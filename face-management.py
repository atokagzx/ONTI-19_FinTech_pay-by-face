#!/usr/bin/env python

import cognitive_face as cf
import cv2 as cv 
from json import load
import sys


with open("faceapi.json") as api:
    data = load(api)
    key = data["key"]
    base_url = data["serviceUrl"]
    groupID = data["groupId"]

cf.BaseUrl.set(base_url)
cf.Key.set(key)

id_x = 0

def add(video):
    video = cv.VideoCapture(video)
    if video.get(cv.CAP_PROP_FRAME_COUNT) < 5:
        print("Video does not contain any face")
        return
    creation = cf.person.create(groupID, id_x)
    id_x += 1
    person_id = creation["personId"]
    shift = video.get(cv.CAP_PROP_FRAME_COUNT) // video.get(cv.CAP_PROP_FPS) // 5
    for i in range(5): 
        video.set(cv.CAP_PROP_POS_FRAMES, shift * i)
        res, frame = video.read()
        cv.imwrite("frame{}.jpg".format(i), frame)
        face_det = cf.face.detect("frame{}.jpg".format(i))
        if len(face_det) == 0:
            print("Video does not contain any face")
            return
    try:
        cf.person_group.create(groupID)
    except:
        pass
    print("5 frames extracted")
    print("PersonId:", person_id)
    print("FaceIds")
    print("=======")
    for i in range(5):
        face_id = cf.person.add_face("frame{}.jpg".format(i), groupID, person_id)
        print(face_id["persistedFaceId"])
        

if sys.argv[1] == "--simple-add":
    video = sys.argv[2]
    add(video)