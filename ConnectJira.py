from cmath import log
import requests
from requests.auth import HTTPBasicAuth
import json
import streamlit as st

personalDomain = st.secrets["personalDomain"]
personalEmail = st.secrets["personalEmail"]
personalToken = st.secrets["personalToken"]


def connecJiraPython(url, method):
    auth = HTTPBasicAuth(personalEmail, personalToken)
    headers = {
        "Accept": "application/json"
    }
    response = requests.request(
        method,
        url,
        headers=headers,
        auth=auth
    )
    dictResponse = json.loads(response.text)
    return dictResponse


def getAllProjects():
    url = personalDomain+"rest/api/latest/project"
    method = 'GET'
    response = connecJiraPython(url, method)
    return response


def getAllIssuesByProject(projectKey, type, start):
    url = personalDomain+"rest/api/latest/search?jql=project=" + \
        projectKey+"%20and%20issuetype="+type+"&maxResults=100&startAt=" + \
        str(start)
    method = 'GET'
    response = connecJiraPython(url, method)
    return response

### Recupera Storys, Task, Subtasks y Defects de un proyecto
def getAllIssuesTypesByProject(projectKey, start):
    ###Solo para element
    # url = personalDomain+"rest/api/latest/search?jql=project=" + \
    #     projectKey+"%20and%20issuetype%20in%20(Story,Task,Sub-task,Defect)&maxResults=100&startAt=" + \
    #     str(start)
    ###Para sus dominios normales
    url = personalDomain+"rest/api/latest/search?jql=project=" + \
        projectKey+"%20and%20issuetype%20in%20(Story,Task,Sub-task,Bug)&maxResults=100&startAt=" + \
        str(start)
    method = 'GET'
    response = connecJiraPython(url, method)
    return response

def getBoardFromProject(projectKey):
    url = personalDomain+"rest/agile/1.0/board?projectKeyOrId="+projectKey
    method = 'GET'
    response = connecJiraPython(url, method)
    return response


def getSprintsByIdBoard(boardId):
    url = personalDomain+"rest/agile/1.0/board/" + \
        str(boardId)+"/sprint"
    method = 'GET'
    response = connecJiraPython(url, method)
    return response


def getIssuesBySprint(sprintId, start):
    # url = personalDomain+"rest/agile/1.0/sprint/" + \
    #     str(sprintId)+"/issue?jql=issuetype=Story&maxResults=100&startAt=" + \
    #     str(start)
    url = personalDomain+"rest/agile/1.0/sprint/" + \
        str(sprintId)+"/issue?jql=issuetype%20in%20(Story,Task)&maxResults=100&startAt=" + \
        str(start)
    method = 'GET'
    response = connecJiraPython(url, method)
    return response


# def getIssueById(IssueId):
#    url = personalDomain+"rest/api/latest/search?jql=parent="+IssueId
#    method = 'GET'
#    response = connecJiraPython(url, method)
#
#    return response

def getIssueById(IssueId):
    url = personalDomain+"rest/api/latest/issue/"+IssueId
    method = 'GET'
    response = connecJiraPython(url, method)

    return response


def getIssueByParentId(IssueParentId, start):
    url = personalDomain+"rest/api/latest/search?jql=parent=" + \
        IssueParentId+"&maxResults=100&startAt="+str(start)
    method = 'GET'
    response = connecJiraPython(url, method)

    return response


def getFields():
    url = personalDomain+"rest/api/3/field"
    method = 'GET'
    response = connecJiraPython(url, method)
    return response


def getIssueById(IssueId):
    url = personalDomain+"rest/api/latest/issue/"+IssueId
    method = 'GET'
    response = connecJiraPython(url, method)
    return response