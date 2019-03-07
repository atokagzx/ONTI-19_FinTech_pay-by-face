#!/usr/bin/env python

### VER 1.5 ###

### <file-like object> ###
class FrameFileObject:   
    def __init__(self, data):
        import cv2
        self.data = cv2.imencode('.png', data)[1].tostring()
    
    def read(self):
        return self.data
### </file-like object> ###

class FaceAPIsession():
    import cognitive_face as cf

    def __init__(self, key, baseURL, group):
        errorMessage = ''

        if key == '' or key == None:
            errorMessage += 'key;'
        if baseURL == '' or baseURL == None:
            errorMessage += 'baseURL;'
        if group == '' or group == None:
            errorMessage += 'group;'
        if errorMessage != '':
            raise EmptyArgumentsError(errorMessage)

        self.group = group
        self.__key = key
        self.__baseURL = baseURL

        self.ApplySettings()
    
    def UpdateGroup(self, group):
        self.group = group

    def UpdateKey(self, key):
        self.__key = key
    
    def UpdateBaseURL(self, baseURL):
        self.__baseURL = baseURL

    def ApplySettings(self):
        cf.Key.set(self.__key)
        cf.BaseUrl.set(self.__baseURL)

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

class ArgumentFormatErro(Exception):
    def __init__(self, message = ''):
        self.message = message
### </Сustom errors> ###

import cognitive_face as cf

### <Auxiliary functions> ###
def GetFrames(path, start = 0.0, end = 1.0, step = 0.25):
    import cv2

    cap = cv2.VideoCapture(path)
    result = []
    
    if cap.get(7) < 5:
        raise FramesCountError('Video does not contain any face')

    for x in [start + step * i for i in range(int((end - start) // step) + 1)]:
        cap.set(1, x)
        _, frame = cap.read()
        result.append(FrameFileObject(frame))

    return result


def GetIDs(session, frames):
    result = []

    for x in frames:
        for y in cf.face.detect(x):
            result.append(y['faceId'])

    if len(result) != 5:
        raise FacesCountError()

    return result


def FindID(session, id):
    for x in cf.person.lists(session.group):
        if x['personId'] == id:
            return True
    return False   


def GetPersonID(session, name):
    personID = ''
    for x in cf.person.lists(session.group):
        if x['name'] == name:
            personID = x['personId']
            break
    if personID == '':
        raise PersonExistError()
    return personID


def GetPersonName(session, personID):
    personName = ''

    for x in cf.person.lists(session.group):
        if x['personId'] == personID:
            personName = x['name']
            break
    if personName == '':
        raise PersonExistError()
    return personName


def CountFaces(session, frames):
    count = 0
    allFramesHaveFace = True
    for x in frames:
        temp = cf.face.detect(x)
        count += len(temp)
        if len(temp) == 0:
            allFramesHaveFace = False

    return count, allFramesHaveFace


def CheckFaces(session, frames):
    if len(frames) == 0:
        raise FacesCountError()

def CheckFace(session, frame):
    if len(cf.face.detect(frame)) == 0:
        return False
    else:
        return True
### </Auxiliary functions> ###

### <Main functions> ###
def CreateGroup(session):
    try:
        cf.person_group.create(session.group)
    except:
        pass


def CreatePerson(session, name, video):
    CheckFaces(session, GetFrames(video))
    try:
        GetPersonID(session, name)
        raise PersonExistError('Person {0} already exist'.format(name))
    except:
        pass
    cf.person.create(session.group, name, False)
    personID = GetPersonID(session, name)
    facesID, count = UploadFaces(session, personID, video)

    return personID, facesID, count


def CreateAnonPerson(session, video):
    CheckFaces(session, GetFrames(video))
    try:
        number = str(max([int(x['personId']) for x in cf.person.lists(session.group) if x['personId'].isdigit()]) + 1)
    except:
        number = '0'
    cf.person.create(session.group, number, False)
    personID = GetPersonID(session, number)
    facesID, count = UploadFaces(session, personID, video)

    return personID, facesID, count


def UploadFaces(session, personID, video, check=True):
    frames = [x for x in GetFrames(video) if CheckFace(session, x)]
    if check:
        CheckFaces(session, frames)
    facesID = []
    for frame in frames:
        facesID.append(cf.person.add_face(frame, session.group, personID))

    return facesID, len(facesID)


def AddNewFaces(session, personName, video):
    personID = GetPersonID(session, personName)
    faces = [x for x in GetFrames(video) if CheckFace(session, x)]
    facesID = []
    for x in faces:
        facesID.append(cf.person.add_face(x, session.group, personID))
    return facesID, len(facesID)


def DeletePerson(session, personID = None, personName = None):
    if personID == None and personName == None:
        raise EmptyArgumentsError('personID;personName')
    if personID != None:
        cf.person.delete(session.group, personID)
    else:
        personID = GetPersonID(session, personName)
        cf.person.delete(session.group, personID)

    return personID


def StartTrain(session):
    personCount = len(cf.person.lists(session.group))
    cf.person_group.train(session.group)

    return personCount


def IdentifyPerson(session, video, minDegree = 0.499999999999999):
    try:
        status = cf.person_group.get_status(session.group)['status']
    except:
        raise SystemReadinessError()

    if status != 'succeeded':
        raise SystemReadinessError()

    IDs = GetIDs(session, GetFrames(video))
    personID = ''
    for x in cf.face.identify(IDs, session.group, threshold=0.5):
        if len(x['candidates']) == 0:
            raise LowDegreeOfConfidenceError()
        if personID == '':
            personID = x['candidates'][0]['personId']
        else:
            if personID != x['candidates'][0]['personId']:
                raise LowDegreeOfConfidenceError()
        return GetPersonName(session, personID)


def GetPersonList(session):
    return [x['personId'] for x in cf.person.lists(session.group)]


def UpdateGroupData(session, data):
    if type(data) != type(''):
        raise InvalidArgumentError('data;')
    cf.person_group.update(session.group, session.group, data)


#def CheckGroupStatus(sesssion):

### </Main functions> ###