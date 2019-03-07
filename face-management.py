#!/usr/bin/env python

### Put your code below this comment ###
import AzureCSLib as az
import sys
def GetParams():
    import json
    with open('faceapi.json') as jsonFile:
        key = json.load(jsonFile)['key']
    with open('faceapi.json') as jsonFile:
        group = json.load(jsonFile)['groupId']
    with open('faceapi.json') as jsonFile:
        baseURL = json.load(jsonFile)['serviceUrl']
    return az.FaceAPIsession(key, baseURL, group)


def US004(session, video):
    try:
        personID, facesID, count = az.CreateAnonPerson(session, video)
        az.UpdateGroupData(session, "Updated")
        print('{1} frames extracted{0}PersonId: {2}{0}FaceIds{0}======={0}{3}'.format('\n', count, personID, '\n'.join([x['persistedFaceId'] for x in facesID])))
    except (az.FacesCountError, az.FramesCountError):
        print('Video does not contain any face')
    except az.PersonExistError as exc:
        print(exc.message)


def US006(session):
    print('\n'.join(az.GetPersonList(session)))


def US007(session, personID):
    try:
        az.DeletePerson(session, personID=personID)
        az.UpdateGroupData(session, "Updated")
    except az.PersonExistError:
        print('Person with id {0} does not exist'.format(personID))

#def US008(session, )


def Main():
    session = GetParams()
    az.CreateGroup(session)
    temp = sys.argv
    print(temp[1])
    print(temp[2])
    if temp[1] == '--simple-add':
        US004(session, temp[2])


Main()
