#!/usr/bin/env python

### VER 2.3 ###

import cognitive_face as cf
import numpy as np
import dlib as dl
import cv2
from FrameFileObject import FrameFileObject as flo

### <Сustom errors> ###
class FramesCountError(Exception):
    def __init__(self, message = ''):
        self.message = message

class FacesCountError(Exception):
    def __init__(self, message = ''):
        self.message = message

class PersonExistError(Exception):
    def __init__(self, message = ''):
        self.message = message

class LowDegreeOfConfidenceError(Exception):
    def __init__(self, message = ''):
        self.message = message

class SystemReadinessError(Exception):
    def __init__(self, message = ''):
        self.message = message

class EmptyArgumentsError(Exception):
    def __init__(self, message = ''):
        self.message = message

class InvalidArgumentError(Exception):
    def __init__(self, message = ''):
        self.message = message

class ArgumentFormatError(Exception):
    def __init__(self, message = ''):
        self.message = message

class PersonGroupExistError(Exception):
    def __init__(self, message = ''):
        self.message = message

class PersonGroupTrainingError(Exception):
    def __init__(self, message = ''):
        self.message = message
### </Сustom errors> ###

class FaceAPIsession():
    def __init__(self, key, baseURL, group, dlibPreditor="shape_predictor_68_face_landmarks.dat"):
        errorMessage = ''

        if key == '' or key == None:
            errorMessage += 'key;'
        if baseURL == '' or baseURL == None:
            errorMessage += 'baseURL;'
        if group == '' or group == None:
            errorMessage += 'group;'
        if errorMessage != '':
            raise EmptyArgumentsError(errorMessage)

        self.detector = dl.get_frontal_face_detector()
        try:
            self.predictor = dl.shape_predictor(dlibPreditor)
        except:
            self.predictor = dl.shape_predictor("D:/shape_predictor_68_face_landmarks.dat")

        self.group = group
        self.__key = key
        self.__baseURL = baseURL

        self.OpenConnection()
    
    def UpdateGroup(self, group):
        self.group = group

    def UpdateKey(self, key):
        self.__key = key
    
    def UpdateBaseURL(self, baseURL):
        self.__baseURL = baseURL

    def OpenConnection(self):
        cf.Key.set(self.__key)
        cf.BaseUrl.set(self.__baseURL)

### <Auxiliary functions> ###
    def GetFrames(self, path, start = 0.0, end = 1.0, step = 0.25):
        import cv2

        cap = cv2.VideoCapture(path)
        result = []
        
        if cap.get(7) < 5:
            raise FramesCountError('Video does not contain any face')

        for x in [start + step * i for i in range(int((end - start) // step) + 1)]:
            cap.set(1, x)
            _, frame = cap.read()
            result.append(flo(frame))

        return result

    def GetIDs(self, frames):
        self.OpenConnection()
        result = []

        for x in frames:
            for y in cf.face.detect(x):
                result.append(y['faceId'])

        if len(result) != 5:
            raise FacesCountError()

        return result

    def FindID(self, id):
        self.OpenConnection()
        for x in cf.person.lists(self.group):
            if x['personId'] == id:
                return True
        return False   

    def GetPersonID(self, name):
        self.OpenConnection()
        personID = ''
        for x in cf.person.lists(self.group):
            if x['name'] == name:
                personID = x['personId']
                break
        if personID == '':
            raise PersonExistError()
        return personID

    def GetPersonName(self, personID):
        self.OpenConnection()
        personName = ''

        for x in cf.person.lists(self.group):
            if x['personId'] == personID:
                personName = x['name']
                break
        if personName == '':
            raise PersonExistError()
        return personName

    def CountFaces(self, frames):
        allFramesHaveFace = True
        for x in frames:
            temp = self.detector(cv2.imdecode(x.getBuff, -1))
            count += len(temp)
            if len(temp) == 0:
                allFramesHaveFace = False

        return count, allFramesHaveFace

    def CountPersons(self):
        return len(cf.person.lists(self.group))

    def CheckFaces(self, frames):
        for x in frames:
            if self.CheckFace(x):
                return
        raise FacesCountError()

    def CheckFace(self, frame):
        detected = self.detector(cv2.imdecode(frame.getBuff(), -1))
        if len(detected) == 0:
            return False
        else:
            return True

    def CheckGroupUpdation(self):
        self.OpenConnection()
        if self.GetGroupData() == 'Updated':
            return True
        else:
            return False

    def CheckGroupExist(self):
        self.OpenConnection()
        try:
            cf.person_group.get(self.group)
        except cf.CognitiveFaceException as cfe:
            if cfe.code == 'PersonGroupNotFound':
                raise PersonGroupExistError('The group does not exist')

    def AddPersonData(self, id, phone):
        self.OpenConnection()
        for x in cf.person.lists(self.group):
            if x['personId'] == id:
                cf.person.update(self.group, id, user_data = phone)
                return
        raise PersonExistError('No person with id "{0}"'.format(id))

    def FindPersonByData(self, data, dataType):
        self.OpenConnection()
        IDs = []
        for x in cf.person.lists(self.group):
            if x['userData'] == data:
                IDs.append(x['personId'])
        if len(IDs) == 0:
            raise PersonExistError('No person with {1} "{0}"'.format(data, dataType))
        return IDs

    def GetPersonData(self, personID):
        self.OpenConnection()
        return cf.person.get(self.group, personID)['userData']

    def UpdatePersonData(self, personID, data=''):
        self.OpenConnection()
        cf.person.update(self.group, personID, user_data=data)

    def CheckGroupTraining(self):
        try:
            return True if cf.person_group.get_status(self.group)['status'] == 'success' else False
        except cf.CognitiveFaceException as cfe:
            if cfe.code == 'PersonGroupNotTrained':
                raise PersonGroupTrainingError()
            else:
                raise cf.CognitiveFaceException(cfe.status_code, cfe.code, cfe.msg)
### </Auxiliary functions> ###

### <Main functions> ###
    def CreateGroup(self):
        self.OpenConnection()
        try:
            cf.person_group.create(self.group)
        except:
            pass

    def CreatePerson(self, video = None, frames = None, name = None, data = None):
        self.OpenConnection()

        if video != None or frames != None:
            frames = self.GetFrames(video) if frames == None else frames
            self.CheckFaces(frames)
            video = ''

        self.CreateGroup()
        if name != None:
            try:
                self.GetPersonID(name)
                raise PersonExistError('Person {0} already exist'.format(name))
            except:
                pass
        else:
            try:
                name = str(max([int(x['name']) for x in cf.person.lists(self.group) if x['name'].isdigit()]) + 1)
            except:
                name = '0'
        cf.person.create(self.group, name)
        personID = self.GetPersonID(name)
        if video != None :
            facesID, count = self.UploadFaces(personID, frames)
            return personID, facesID, count
        else:
            return personID

    def UploadFaces(self, personID, frames, check=True):
        self.OpenConnection()
        if check:
            self.CheckFaces(frames)
        facesID = []
        for frame in frames:
            facesID.append(cf.person.add_face(frame, self.group, personID)['persistedFaceId'])

        return facesID, len(facesID)

    def AddNewFaces(self, personName, video):
        self.OpenConnection()
        personID = self.GetPersonID(personName)
        faces = [x for x in self.GetFrames(video) if self.CheckFace(x)]
        facesID = []
        for x in faces:
            facesID.append(cf.person.add_face(x, self.group, personID))
        return facesID, len(facesID)

    def DeletePerson(self, personID = None, personName = None):
        self.OpenConnection()
        if personID == None and personName == None:
            raise EmptyArgumentsError('personID;personName')
        if personID != None:
            self.GetPersonName(personID)
            cf.person.delete(self.group, personID)
        else:
            personID = self.GetPersonID(personName)
            cf.person.delete(self.group, personID)

        return personID

    def StartTrain(self):
        self.OpenConnection()
        personCount = len(cf.person.lists(self.group))
        cf.person_group.train(self.group)

        return personCount

    def IdentifyPerson(self, video=None, frames=None, minDegree = 0.5):
        self.OpenConnection()

        try:
            status = cf.person_group.get_status(self.group)['status']
        except:
            raise SystemReadinessError()

        if status != 'succeeded':
            raise SystemReadinessError()

        if video == None and frames == None:
            raise EmptyArgumentsError('video;frames')

        IDs = self.GetIDs(self.GetFrames(video) if video != None else frames)

        personID = ''

        for x in cf.face.identify(IDs, self.group, threshold=0.5):

            if len(x['candidates']) == 0:
                raise LowDegreeOfConfidenceError()

            if personID == '':
                personID = x['candidates'][0]['personId']

            else:
                if personID != x['candidates'][0]['personId']:
                    raise LowDegreeOfConfidenceError()

            return personID

    def GetPersonList(self):
        self.OpenConnection()
        return [x['personId'] for x in cf.person.lists(self.group)]

    def UpdateGroupData(self, data):
        self.OpenConnection()

        if type(data) != type(''):
            raise InvalidArgumentError('data;')

        cf.person_group.update(self.group, self.group, data)

    def GetGroupData(self):
        self.OpenConnection()
        return cf.person_group.get(self.group)['userData'] 

    def DeleteGroup(self):
        self.OpenConnection()
        self.CheckGroupExist()

        cf.person_group.delete(self.group)

        return True  
### </Main functions> ###