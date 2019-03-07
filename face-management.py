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


def SimpleAdd(session, video):
    try:
        personID, facesID, count = az.CreateAnonPerson(session, video)
        az.UpdateGroupData(session, "Updated")
        print('{1} frames extracted{0}PersonId: {2}{0}FaceIds{0}======={0}{3}'.format('\n', count, personID, '\n'.join([x['persistedFaceId'] for x in facesID])))
    except (az.FacesCountError, az.FramesCountError):
        print('Video does not contain any face')
    except az.PersonExistError as exc:
        print(exc.message)


def GetPersonList(session):
    print('\n'.join(az.GetPersonList(session)))


def DeletePerson(session, personID):
    try:
        az.DeletePerson(session, personID=personID)
        az.UpdateGroupData(session, "Updated")
    except az.PersonExistError:
        print('Person with id {0} does not exist'.format(personID))

def Train(session):
    if az.CheckGroupUpdation(session):
        print('Training task for {0} persons started'.format(az.StartTrain(session)))
        az.UpdateGroupData(session, 'Don\'t updated')
    else:
        print('System does not updated')


def Main():
    session = GetParams()
    az.CreateGroup(session)
    temp = sys.argv
    if temp[1] == '--simple-add':
        SimpleAdd(session, temp[2])


Main()
