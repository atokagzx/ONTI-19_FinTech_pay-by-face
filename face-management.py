#!/usr/bin/env python

### Put your code below this comment ###
import AzureCSLib as az
import sys 

def GetParams():
    import json
    with open('faceapi.json') as jsonFile:
        temp = json.load(jsonFile)
        key = temp['key']
        group = temp['groupId']
        baseURL = temp['serviceUrl']
    return az.FaceAPIsession(key, baseURL, group, "/opt/shape_predictor_68_face_landmarks.dat")

def SimpleAdd(session, video):
    try:
        temp = session.GetFrames(video)
        session.CheckFaces(temp)
        try:
            session.IdentifyPerson(frames=temp)
            print('The same person already exists.')
        except:
            personID, facesID, count = session.CreatePerson(frames=temp)
            session.UpdateGroupData("Updated")
            print('{1} frames extracted{0}PersonId: {2}{0}FaceIds{0}======={0}{3}'.format('\n', count, personID, '\n'.join(facesID)))
    except (az.FacesCountError, az.FramesCountError):
        print('Video does not contain any face')
    except az.PersonExistError as exc:  
        print(exc.message)

def GetPersonList(session):
    try:
        session.CheckGroupExist()
        if session.CountPersons() == 0:
            print('No persons found')
        else:
            print('Persons IDs:\n{0}'.format('\n'.join(session.GetPersonList())))
    except az.PersonGroupExistError as pgee:
        print(pgee.message)

def DeletePerson(session, personID):
    try:
        session.CheckGroupExist()
        session.DeletePerson(personID=personID)
        session.UpdateGroupData("Updated")
        print('Person deleted')
    except az.PersonGroupExistError:
        print('The group does not exist')
    except az.PersonExistError:
        print('The person does not exist')

def Train(session):
    def temp():
        if session.CheckGroupUpdation():
            session.UpdateGroupData('Do not updated')
            if session.CountPersons() == 0:
                print('There is nothing to train')
            else:
                session.StartTrain()
                print('Training successfully started')
        else:
            if session.CountPersons() == 0:
                print('There is nothing to train')
            else:
                print('Already trained')

    try:
        session.CheckGroupExist()
        try:
            if not session.CheckGroupTraining():
                temp()
            else:
                if session.CheckGroupUpdation():
                    session.UpdateGroupData('Do not updated')
                    session.StartTrain()
                    print('Training successfully started')
                else:
                    print('Already trained')
        except:
            temp()
    except az.PersonGroupExistError:
        print('There is nothing to train')

def UnsaveAuth(session, video):
    import os
    import json
    try:
        session.CheckGroupExist()
        if session.CheckGroupUpdation():
            print('The service is not ready')
            try:
                os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'person.json'))
            except:
                pass
        else:
            personID = session.IdentifyPerson(video)
            print('{0} identified'.format(personID))
            with open('person.json', 'w') as jsonF:
                json.dump({ "id" : personID }, jsonF)
    except az.PersonGroupExistError:
        print('The service is not ready')
    except az.SystemReadinessError:
        print('System does not trained')
    except az.LowDegreeOfConfidenceError:
        print('The person was not found')
    except (az.FramesCountError, az.FacesCountError):
        print('The video does not follow requirements')

def DeleteGroup(session):
    try:
        session.DeleteGroup()
        print('Group was deleted')
    except az.PersonGroupExistError:
        print('Group does not exist')

def Main():
    session = GetParams()
    temp = sys.argv
    if temp[1] == '--simple-add':
        SimpleAdd(session, temp[2])
    elif temp[1] == '--list':
        GetPersonList(session)
    elif temp[1] == '--del':
        DeletePerson(session, temp[2])
    elif temp[1] == '--train':
        Train(session)
    elif temp[1] == '--find':
        UnsaveAuth(session, temp[2])
    elif temp[1] == '--delgr':
        DeleteGroup(session)
    elif temp[1] == '--stat':
        print(session.GetGroupData())
Main()