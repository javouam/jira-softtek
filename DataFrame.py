from array import array
from cmath import nan
from datetime import datetime
from math import floor
from multiprocessing.dummy import Array
from numbers import Number
from os import truncate
from pickle import FALSE
from tracemalloc import start
import numpy as np
import pandas as pd
import streamlit as st
import ConnectJira
from datetime import datetime


def getStartAt(response):
    total = response['total']
    maxResults = response['maxResults']
    startAt = response['startAt']
    allStartAt = [0]
    while total > (startAt+maxResults):
        startAt = startAt+maxResults
        allStartAt.append(startAt)
    return allStartAt


def getCustomFields():
    customFields = {}
    fields = ConnectJira.getFields()
    for field in fields:
        if (field['name'] == 'Story Points') | (field['name'] == 'Story points'):
            customFields['Story_Points'] = field['key']
        if field['name'] == 'Sprint':
            customFields['Sprint'] = field['key']
        if field['name'] == 'Defect Type':
            customFields['Defect_Type'] = field['key']
        if field['name'] == 'Detection Phase':
            customFields['Detection_Phase'] = field['key']
        if field['name'] == 'Injection Phase':
            customFields['Injection_Phase'] = field['key']
    return customFields


def getStoryPointsPerStory(projectKey, Story_Points):
    listRows = []
    pagination = getStartAt(
        ConnectJira.getAllIssuesByProject(projectKey, "Story", 0))
    for index in pagination:
        storys: dict = ConnectJira.getAllIssuesByProject(
            projectKey, "Story", index)
        for story in storys['issues']:
            row = {}
            row['id_story'] = story['id']
            if story['fields'][Story_Points] != None:
                row['story_points'] = story['fields'][Story_Points]
            else:
                row['story_points'] = 0
            listRows.append(row)
    return listRows


def getInfoIssuesIntoSprints(projectKey: str, boardName):
    dataRows = []
    dataSprints: dict = {}

    customFields: dict = getCustomFields()
    Story_Points: str = customFields['Story_Points']
    Sprints: str = customFields['Sprint']
    storyPointsByStory = getStoryPointsPerStory(projectKey, Story_Points)

    data: dict = ConnectJira.getBoardFromProject(projectKey)
    if 'values' in data:
        for dataBoard in data['values']:
            if boardName == dataBoard['name']:
                sprints = ConnectJira.getSprintsByIdBoard(dataBoard['id'])

                if 'values' in sprints:
                    for dataSprint in sprints['values']:
                        dataSprint: dict = {
                            'id': dataSprint['id'],
                            'name': dataSprint['name'],
                            'state': dataSprint['state'],
                            'startDate': dataSprint['startDate'][0:10],
                            'endDate': dataSprint['endDate'][0:10]
                        }
                        dataSprints[dataSprint['id']] = dataSprint

    listIssueTypes = ["Sub-task", "Story", "Task"]
    # listIssueTypes = ["Sub-task"]

    for issueType in listIssueTypes:

        pagination = getStartAt(
            ConnectJira.getAllIssuesByProject(projectKey, issueType, 0))

        for index in pagination:
            subtasksInProject: dict = ConnectJira.getAllIssuesByProject(
                projectKey, issueType, index)
            if len(subtasksInProject['issues']) > 0:
                for subtask in subtasksInProject['issues']:
                    subtaskDetail = ConnectJira.getIssueById(subtask['id'])
                    if subtaskDetail['fields'][Sprints] != None:
                        for sprint in subtaskDetail['fields'][Sprints]:
                            sprintId = sprint['id']
                            sprintName = sprint['name']
                            if len(subtaskDetail['fields']['worklog']['worklogs']) > 0:
                                for wl in subtaskDetail['fields']['worklog']['worklogs']:
                                    timeSpentByUser = float(
                                        wl['timeSpentSeconds'] if wl['timeSpentSeconds'] != None else 0) / 3600
                                    updateAuthor = wl['updateAuthor']['displayName']
                                    created = wl['created'][0:10]
                                    work_log_id = wl['id']
                                    rowSubtask = getObjRow(
                                        storyPointsByStory, subtaskDetail, sprintId, sprintName, timeSpentByUser, updateAuthor, created, work_log_id, issueType)
                                    dataRows.append(rowSubtask)
                            else:
                                timeSpentByUser = 0
                                updateAuthor = " "
                                created = " "
                                work_log_id = " "
                                rowSubtask = getObjRow(storyPointsByStory, subtaskDetail, sprintId,
                                                       sprintName, timeSpentByUser, updateAuthor, created, work_log_id, issueType)
                                dataRows.append(rowSubtask)
                    else:
                        sprintId = 0
                        sprintName = "Backlog"
                        if len(subtaskDetail['fields']['worklog']['worklogs']) > 0:
                            for wl in subtaskDetail['fields']['worklog']['worklogs']:
                                timeSpentByUser = float(
                                    wl['timeSpentSeconds'] if wl['timeSpentSeconds'] != None else 0) / 3600
                                updateAuthor = wl['updateAuthor']['displayName']
                                created = wl['created'][0:10]
                                work_log_id = wl['id']
                                rowSubtask = getObjRow(storyPointsByStory, subtaskDetail, sprintId,
                                                       sprintName, timeSpentByUser, updateAuthor, created, work_log_id, issueType)
                                dataRows.append(rowSubtask)
                        else:
                            timeSpentByUser = 0
                            updateAuthor = " "
                            created = " "
                            work_log_id = " "
                            rowSubtask = getObjRow(storyPointsByStory, subtaskDetail, sprintId,
                                                   sprintName, timeSpentByUser, updateAuthor, created, work_log_id, issueType)
                            dataRows.append(rowSubtask)

    df = pd.DataFrame(dataRows)
    # df.to_csv('subtaskWorklogs2.csv')
    # print('subtaskWorklogs2.csv creado correctamente')
    return dataRows, dataSprints


def getObjRow(storyPointsByStory, subtaskDetail, sprintId, sprintName, timeSpentByUser, updateAuthor, created, work_log_id, issueType):
    rowSubtask = {}
    rowSubtask['project'] = subtaskDetail['fields']['project']['name']
    rowSubtask['issue_type'] = issueType
    rowSubtask['issue_id'] = subtaskDetail['id']
    rowSubtask['issue_key'] = subtaskDetail['key']
    rowSubtask['parent_issue_id'] = subtaskDetail['fields']['parent']['id'] if issueType == "Sub-task" else " "
    rowSubtask['summary_issue'] = subtaskDetail['fields']['parent']['fields'][
        'summary'] if issueType == "Sub-task" else subtaskDetail['fields']['summary']
    rowSubtask['story_state'] = subtaskDetail['fields']['parent']['fields']['status'][
        'name'] if issueType == "Sub-task" else subtaskDetail['fields']['status']['name']
    rowSubtask['sprint_id'] = sprintId
    rowSubtask['sprint'] = sprintName
    rowSubtask['assignee'] = subtaskDetail['fields']['assignee'][
        'displayName'] if subtaskDetail['fields']['assignee'] != None else "Unassigneed"
    if storyPointsByStory != []:
        for storyPoints in storyPointsByStory:
            rowSubtask['story_points'] = 0
            if (issueType == "Sub-task"):
                if (storyPoints['id_story'] == subtaskDetail['fields']['parent']['id']):
                    rowSubtask['story_points'] = storyPoints['story_points']
            else:
                if (storyPoints['id_story'] == subtaskDetail['id']):
                    rowSubtask['story_points'] = storyPoints['story_points']
    else:
        rowSubtask['story_points'] = nan
    rowSubtask['original_estimate'] = float(
        subtaskDetail['fields']['timeoriginalestimate'] if subtaskDetail['fields']['timeoriginalestimate'] != None else 0) / 3600
    rowSubtask['time_spent'] = float(
        subtaskDetail['fields']['progress']['progress'] if subtaskDetail['fields']['progress']['progress'] != None else 0) / 3600
    rowSubtask['time_spent_by_user'] = timeSpentByUser
    rowSubtask['updateAuthor'] = updateAuthor
    rowSubtask['created'] = created
    rowSubtask['work_log_id'] = work_log_id
    rowSubtask['time_remaining'] = (float(subtaskDetail['fields']['progress']['total'] if subtaskDetail['fields']['progress']['total'] != None else 0) - float(
        subtaskDetail['fields']['progress']['progress'] if subtaskDetail['fields']['progress']['progress'] != None else 0)) / 3600
    rowSubtask['total_time'] = float(
        subtaskDetail['fields']['progress']['total'] if subtaskDetail['fields']['progress']['total'] != None else 0) / 3600
    return rowSubtask


def createInfoTasksByIssueIntoSprints(dataRows: array):
    columnsFormat: dict = {}

    columnsFormat['story_points'] = '{:.1f}'
    columnsFormat['original_estimate'] = '{:.1f}'
    columnsFormat['time_spent'] = '{:.1f}'
    columnsFormat['time_spent_by_user'] = '{:.1f}'
    columnsFormat['time_remaining'] = '{:.1f}'
    columnsFormat['total_time'] = '{:.1f}'

    df = pd.DataFrame(dataRows)
    # df.to_csv('tasks2.csv')

    return df, columnsFormat


def createInfoBySprint(dataRows: array, dataSprints: dict):
    dataRowsStories = []
    stories: dict = {}
    columnsFormat: dict = {}
    # dataRows, dataSprints = getInfoIssuesIntoSprints(projectKey)

    for data in dataRows:
        dataSprint = dataSprints.get(data['sprint_id'], None)

        time_spent_by_sprint: Number = 0
        if (data['created'] != " ") & (data['sprint'] != "Backlog"):
            if datetime.strptime(dataSprint['startDate'], '%Y-%m-%d') <= datetime.strptime(data['created'], '%Y-%m-%d') <= datetime.strptime(dataSprint['endDate'], '%Y-%m-%d'):
                time_spent_by_sprint = data['time_spent_by_user']

            if data['parent_issue_id'] in stories:
                if (data['work_log_id'] in stories.get(data['parent_issue_id'])['storie_worklogs'][data['parent_issue_id']]) == False:
                    stories.get(data['parent_issue_id'])[
                        'original_estimate'] += data['original_estimate']
                    stories.get(data['parent_issue_id'])[
                        'time_remaining'] += data['time_remaining']
                    stories.get(data['parent_issue_id'])[
                        'total_time'] += data['total_time']

                    stories.get(data['parent_issue_id'])[
                        'storie_worklogs'][data['parent_issue_id']][data['work_log_id']] = data['work_log_id']

                if data['sprint_id'] in stories.get(data['parent_issue_id'])['sprints'][data['parent_issue_id']]:
                    stories.get(data['parent_issue_id'])[
                        'sprints'][data['parent_issue_id']][data['sprint_id']]['time_spent_by_sprint'] += time_spent_by_sprint
                else:
                    stories.get(data['parent_issue_id'])['sprints'][data['parent_issue_id']][data['sprint_id']] = {
                        'sprint_id': data['sprint_id'],
                        'sprint': data['sprint'],
                        'time_spent_by_sprint': time_spent_by_sprint
                    }

            else:
                sprints: dict = {}
                # sprints[data['sprint_id']] = {
                sprints[data['parent_issue_id']] = {data['sprint_id']: {
                    'sprint_id': data['sprint_id'],
                    'sprint': data['sprint'],
                    'time_spent_by_sprint': time_spent_by_sprint
                }
                }

                storieWorklogs: dict = {}
                storieWorklogs[data['parent_issue_id']] = {
                    data['work_log_id']: data['work_log_id']}

                dataStory: dict = {
                    'project': data['project'],
                    'issue_type': data['issue_type'],
                    'summary_issue': data['summary_issue'],
                    'story_state': data['story_state'],
                    'story_points': data['story_points'],
                    'original_estimate': data['original_estimate'],
                    'sprints': sprints,
                    'time_remaining': data['time_remaining'],
                    'total_time': data['total_time'],
                    'storie_worklogs': storieWorklogs
                }

                stories[data['parent_issue_id']] = dataStory

    for key in stories.keys():
        issue: dict = stories.get(key)

        dataRow = {}
        dataRow['project'] = issue.get('project', None)
        dataRow['issue_type'] = issue['issue_type']
        dataRow['summary_issue'] = issue['summary_issue']
        dataRow['story_state'] = issue['story_state']
        dataRow['story_points'] = issue['story_points']
        dataRow['original_estimate_by_storie'] = issue['original_estimate']
        dataRow['total_time_by_subtasks'] = issue['total_time']

        totalTimeSpentByIssue: float = 0.0

        for sprintKey in dataSprints.keys():
            spntId: str = None
            for issueSprintKey in issue['sprints'][key].keys():
                if sprintKey == issueSprintKey:
                    spntId = issueSprintKey

            if spntId != None:
                totalTimeSpentByIssue += issue['sprints'][key].get(spntId)[
                    'time_spent_by_sprint']

                dataRow[dataSprints.get(sprintKey)['name']] = issue['sprints'][key].get(spntId)[
                    'time_spent_by_sprint']
            else:
                dataRow[dataSprints.get(sprintKey)['name']] = np.nan

        dataRow['total_time_spent'] = totalTimeSpentByIssue
        dataRow['time_remaining'] = issue['time_remaining']

        if (totalTimeSpentByIssue + issue['time_remaining']) != 0:
            dataRow['porcentaje_avance'] = (totalTimeSpentByIssue /
                                            (totalTimeSpentByIssue + issue['time_remaining'])) * 100

        dataRowsStories.append(dataRow)

    for sprint in dataSprints.values():
        columnsFormat[sprint['name']] = '{:.1f}'

    columnsFormat['story_points'] = '{:.1f}'
    columnsFormat['original_estimate_by_storie'] = '{:.1f}'
    columnsFormat['time_spent'] = '{:.1f}'
    columnsFormat['time_spent_by_user'] = '{:.1f}'
    columnsFormat['total_time_spent'] = '{:.1f}'
    columnsFormat['time_remaining'] = '{:.1f}'
    columnsFormat['total_time_by_subtasks'] = '{:.1f}'
    columnsFormat['porcentaje_avance'] = '{:.1f}%'

    df = pd.DataFrame(dataRowsStories)
    # df.to_csv("dataRowsStories.csv", index=False)
    df2 = df.style.apply(highlight, axis=1)
    return df2, columnsFormat


def highlight(s):
    # blue task
    if s.issue_type == "Task":
        return ['background-color: #7AA6EA']*s.size
    # Green Story
    if s.issue_type == "Story":
        return ['background-color: #76D7C4']*s.size

    if s.issue_type == "Sub-task":
        if np.isnan(s.story_points) == True:
            # blue
            return ['background-color: #85C1E9']*s.size
        else:
            # green
            return ['background-color: #A1F9C3']*s.size


def createDfStoriesBySprint(df_sprint):
    sumaStoryPopints = df_sprint.groupby(["Project_key", "Issue_Status"])[
        "Issue_story_points"].agg(sum="sum").reset_index().loc[:, "sum"].apply(int)
    stories_by_sprint_temp = df_sprint.groupby(["Project_key", "Sprint_name", "Issue_Status"])[
        "Issue_Status"].agg(count="count").reset_index()
    stories_by_sprint = stories_by_sprint_temp.assign(
        Story_Points=sumaStoryPopints)
    return stories_by_sprint


def createDfBugsDefectType(df_all_bugs, type):
    if type == "Defect_Type":
        df_bugs = df_all_bugs.groupby(["Project", "Sprint_Name", "Defect_Type"])[
            "Defect_Type"].agg(count="count").reset_index()

    if type == "Detection_Phase":
        df_bugs = df_all_bugs.groupby(["Project", "Sprint_Name", "Detection_Phase"])[
            "Detection_Phase"].agg(count="count").reset_index()

    if type == "Injection_Phase":
        df_bugs = df_all_bugs.groupby(["Project", "Sprint_Name", "Injection_Phase"])[
            "Injection_Phase"].agg(count="count").reset_index()

    return df_bugs


def createDfByInfoJira(projectKey):
    listRows = []
    listRowsStatus = []
    listSprints = []
    fields = getCustomFields()
    for board in ConnectJira.getBoardFromProject(projectKey)['values']:
        if 'values' in ConnectJira.getSprintsByIdBoard(board['id']).keys():
            for sprint in ConnectJira.getSprintsByIdBoard(board['id'])['values']:

                rowSprint = {}
                rowSprint["Sprint_name"] = sprint["name"]
                rowSprint["Sprint_state"] = sprint["state"]
                rowSprint["Sprint_start_date"] = sprint["startDate"]
                rowSprint["Sprint_end_date"] = sprint["endDate"]
                listSprints.append(rowSprint)

                allStartAt = getStartAt(
                    ConnectJira.getIssuesBySprint(sprint['id'], 0))

                for start in allStartAt:
                    res = ConnectJira.getIssuesBySprint(
                        sprint['id'], start)['issues']
                    if len(res) != 0:
                        for issue in res:
                            # if issue['fields']['issuetype']['name'] == 'Story':
                            row = {}
                            rowSprint = {}
                            row["Project_key"] = projectKey
                            row["Board_name"] = board["name"]
                            row["Board_id"] = board["id"]
                            row["Sprint_name"] = sprint["name"]
                            row["Sprint_id"] = sprint['id']
                            row["Issue_key"] = issue["key"]
                            row["Issue_Type"] = issue['fields']['issuetype']['name']
                            status = issue['fields']['status']['name']
                            if status == "Done":
                                row["Issue_Status"] = "In Progress"
                                listRowsStatus.append(issue["key"])
                            else:
                                row["Issue_Status"] = status
                            row["Issue_summary"] = issue['fields']['summary']
                            if issue['fields']['issuetype']['name'] == 'Story':
                                row["Issue_story_points"] = issue['fields'][fields['Story_Points']]
                            listRows.append(row)
    listRowsStatus = list(set(listRowsStatus))
    for key in listRowsStatus:
        cont = 0
        pos = 0
        for row in listRows:
            cont = cont+1
            if key == row['Issue_key']:
                pos = cont
        if (pos != 0) & (key == listRows[pos-1]['Issue_key']):
            listRows[pos-1]['Issue_Status'] = "Done"

    df = pd.DataFrame(listRows)
    # df.to_excel("DFInfoJira.xlsx", index=False)
    # print('DFInfoJira.xlsx creado correctamente')
    return df, listSprints


def createDfAllIssuesByProject(projectKey):
    listRows = []
    sprits = []
    setSprints = []
    fields = getCustomFields()
    allStartAt = getStartAt(
        ConnectJira.getAllIssuesByProject(projectKey, "Story", 0))

    for start in allStartAt:
        response_all_issues = ConnectJira.getAllIssuesByProject(
            projectKey, "Story", start)
        if len(response_all_issues['issues']) > 0:
            for issue in response_all_issues['issues']:
                row = {}
                row['Key'] = issue['key']
                row['Summary'] = issue['fields']['summary']
                row['Type'] = issue['fields']['issuetype']['name']
                row['Status'] = issue['fields']['status']['name']

                if issue['fields'][fields['Sprint']] != None:

                    lenSprint = len(issue['fields'][fields['Sprint']])
                    if lenSprint == 1:
                        sprits.append(
                            issue['fields'][fields['Sprint']][0]['name'])
                        setSprints.append(
                            issue['fields'][fields['Sprint']][0]['name'])
                    else:
                        for sprint in sorted(issue['fields'][fields['Sprint']],
                                             key=lambda sprint: sprint['startDate']):
                            sprits.append(sprint['name'])
                            setSprints.append(sprint['name'])
                    row['Sprint_Name'] = ",".join(sprits)
                    sprits = []
                else:
                    row['Sprint_Name'] = ""
                if fields['Story_Points'] in issue['fields'].keys():
                    row['Story_Points'] = issue['fields'][fields['Story_Points']]
                else:
                    row['Story_Points'] = 0
                listRows.append(row)

    df = pd.DataFrame(listRows)
    # df.to_excel("allIssues.xlsx", index=False)
    # print('allIssues.xlsx creado correctamente')
    return df, set(setSprints)

def createDfAllIssuesTypesByProject(projectKey):
    listRows = []
    sprits = []
    setSprints = []
    fields = getCustomFields()
    allStartAt = getStartAt(
        ConnectJira.getAllIssuesTypesByProject(projectKey, 0))
   
    for start in allStartAt:
        response_all_issues = ConnectJira.getAllIssuesTypesByProject(
            projectKey, start)
        if len(response_all_issues['issues']) > 0:
            for issue in response_all_issues['issues']:
                row = {}
                row['Key'] = issue['key']
                row['Id_Issue'] = issue['id']
                row['Parent_Id_Issue']= issue['fields']['parent']['id'] if issue['fields']['issuetype']['name'] == "Sub-task" else " "
                row['Summary'] = issue['fields']['summary']
                row['Type'] = issue['fields']['issuetype']['name']
                row['Status'] = issue['fields']['status']['name']
               
                if issue['fields'][fields['Sprint']] != None:
 
                    lenSprint = len(issue['fields'][fields['Sprint']])
                    if lenSprint == 1:
                        sprits.append(
                            issue['fields'][fields['Sprint']][0]['name'])
                        setSprints.append(
                            issue['fields'][fields['Sprint']][0]['name'])
                    else:
                        for sprint in sorted(issue['fields'][fields['Sprint']],
                                             key=lambda sprint: sprint['startDate']):
                            sprits.append(sprint['name'])
                            setSprints.append(sprint['name'])
                    row['Sprint_Name'] = ",".join(sprits)
                    sprits = []
                else:
                    row['Sprint_Name'] = ""
                if fields['Story_Points'] in issue['fields'].keys():
                    row['Story_Points'] = issue['fields'][fields['Story_Points']]
                else:
                    row['Story_Points'] = 0
                row['Time_Original_Estimate']=issue['fields'].get('timeoriginalestimate', 0) / 3600 if issue['fields'].get('timeoriginalestimate') else 0
                row['Time_Spent'] = issue['fields'].get('timespent', 0) / 3600 if issue['fields'].get('timespent') else 0
               
                listRows.append(row)
    df = pd.DataFrame(listRows)
    df.to_csv("allIssueTypesAllSprints.csv", index=False)
    print('allIssueTypesAllSprints.csv creado correctamente')
    return df

def createDfSprintsUSP(dfAllIssues, setSprints, listSprintsStates):
    datos = []
    sprints = list(setSprints)
    for sprint in sprints:
        uspAccepted = 0
        uspCommited = 0
        allUspCommited = 0
        dicRow = {}
        dicRow["Sprint"] = sprint
        for objSprint in listSprintsStates:
            if sprint == objSprint["Sprint_name"]:
                dicRow["State"] = objSprint["Sprint_state"]

        for row in range(int(dfAllIssues.shape[0])):
            sprintsRow = str(dfAllIssues.iloc[row, 4]).split(",")
            if pd.isna(dfAllIssues.iloc[row, 5]) == True:
                usp = 0
            else:
                usp = int(dfAllIssues.iloc[row, 5])
            if sprint in sprintsRow:
                allUspCommited = allUspCommited+usp
                if (sprintsRow[0] == sprint):
                    uspCommited = uspCommited+usp
                if (sprintsRow[0] == sprint) & (len(sprintsRow) == 1) & (str(dfAllIssues.iloc[row, 3]) == 'Done'):
                    uspAccepted = uspAccepted+usp
                if (sprintsRow[len(sprintsRow)-1] == sprint) & (len(sprintsRow) > 1) & (str(dfAllIssues.iloc[row, 3]) == 'Done'):
                    uspAccepted = uspAccepted+usp

        dicRow["Commited Story Points"] = uspCommited
        dicRow["Accepted Story Points"] = uspAccepted
        dicRow["All Commited Story Points"] = allUspCommited
        datos.append(dicRow)

    dfAgileD = pd.DataFrame(datos)
    # dfAgileD.to_excel("USP.xlsx", index=False)
    # print('USP.xlsx creado correctamente')
    return dfAgileD


def createDfBugs(projectKey):
    listRows = []
    sprits = []
    fields = getCustomFields()
    allStartAt = getStartAt(
        ConnectJira.getAllIssuesByProject(projectKey, "Bug", 0))

    for start in allStartAt:
        response_all_bugs = ConnectJira.getAllIssuesByProject(
            projectKey, "Bug", start)
        if len(response_all_bugs['issues']) > 0:
            for issue in response_all_bugs['issues']:
                row = {}
                row['Project'] = issue['fields']['project']['name']
                row['Key'] = issue['key']
                if issue['fields'][fields['Sprint']] != None:
                    lenSprint = len(issue['fields'][fields['Sprint']])
                    if lenSprint == 1:
                        sprits.append(
                            issue['fields'][fields['Sprint']][0]['name'])
                    else:
                        for sprint in issue['fields'][fields['Sprint']]:
                            sprits.append(sprint['name'])
                    row['Sprint_Name'] = ",".join(sprits)
                    sprits = []
                else:
                    row['Sprint_Name'] = "Backlog"
                row['Status'] = issue['fields']['status']['name']
                if issue['fields'][fields['Defect_Type']] != None:
                    row['Defect_Type'] = issue['fields'][fields['Defect_Type']]['value']
                else:
                    row['Defect_Type'] = "null"
                if issue['fields'][fields['Detection_Phase']] != None:
                    row['Detection_Phase'] = issue['fields'][fields['Detection_Phase']]['value']
                else:
                    row['Detection_Phase'] = "null"
                if issue['fields'][fields['Injection_Phase']] != None:
                    row['Injection_Phase'] = issue['fields'][fields['Injection_Phase']]['value']
                else:
                    row['Injection_Phase'] = "null"
                listRows.append(row)
    if len(listRows) > 0:
        df = pd.DataFrame(listRows)
        # df.to_csv("df_all_bugs.csv", index=False)
        # df.to_excel("allBugs.xlsx", index=False)
        # print('df_all_bugs.csv creado correctamente')
        bugs_by_sprint = df.groupby(["Project", "Sprint_Name", "Status"])[
            "Status"].agg(count="count").reset_index()
        return df, bugs_by_sprint
    else:
        return "Aún no han registrado defectos para este proyecto", ""


def createDfTimePerUser(listSprintsStates, dataRows):
    listRows = []
    # dataRows, dataSprints = getInfoIssuesIntoSprints(projectKey)
    for dRow in dataRows:
        for sprint in listSprintsStates:
            startDatesprint = datetime.strptime(
                sprint['Sprint_start_date'][0:10], '%Y-%m-%d')
            endDateSprint = datetime.strptime(
                sprint['Sprint_end_date'][0:10], '%Y-%m-%d')
            diferencia = endDateSprint-startDatesprint
            if dRow["created"] != " ":
                if startDatesprint <= datetime.strptime(dRow["created"], '%Y-%m-%d') <= endDateSprint:
                    if dRow["sprint"] == sprint['Sprint_name']:
                        hrsPerSprint = 8*(round(diferencia.days/7)*5)
                        row = {}
                        row["Project"] = dRow["project"]
                        row["Subtask_Key"] = dRow["issue_key"]
                        row["worklog_id"] = dRow["work_log_id"]
                        row["Sprint_name"] = dRow["sprint"]
                        row["User"] = dRow["updateAuthor"]
                        row["Original_estimate"] = dRow["original_estimate"]
                        row["%PlannedSubtask"] = (
                            dRow["original_estimate"]*100)/hrsPerSprint
                        row["TimeSpentPerUser"] = dRow["time_spent_by_user"]
                        row["%SpentSubtask"] = (
                            dRow["time_spent_by_user"]*100)/hrsPerSprint
                        listRows.append(row)
    df = pd.DataFrame(listRows)
    # df.to_csv("dfTimePerUser2.csv", index=False)
    # print("dfTimePerUser2.csv creado correctamente")
    df_time_per_user = df.groupby(
        by=['Project', 'Sprint_name', 'User']).sum().reset_index()

    columnsFormat: dict = {}
    columnsFormat['Original_estimate'] = '{:.1f}'
    columnsFormat['%PlannedSubtask'] = '{:.1f}%'
    columnsFormat['TimeSpentPerUser'] = '{:.1f}'
    columnsFormat['%SpentSubtask'] = '{:.1f}%'

    return df_time_per_user, columnsFormat


def createDfAssignee(dataRows):
    listRows = []
    for dRow in dataRows:
        if len(listRows) == 0:
            row = {}
            row['project'] = dRow['project']
            row['sprint'] = dRow['sprint']
            row['issue_key'] = dRow['issue_key']
            row['assignee'] = "Assigneed" if dRow['assignee'] != "Unassigneed" else dRow['assignee']
            row['original_estimate'] = dRow['original_estimate']
            listRows.append(row)
        else:
            isAggregate = False
            for lRow in listRows:
                if (lRow['sprint'] == dRow['sprint']) & (lRow['issue_key'] == dRow['issue_key']):
                    isAggregate = True
            if isAggregate == False:
                row = {}
                row['project'] = dRow['project']
                row['sprint'] = dRow['sprint']
                row['issue_key'] = dRow['issue_key']
                row['assignee'] = "Assigneed" if dRow['assignee'] != "Unassigneed" else dRow['assignee']
                row['original_estimate'] = dRow['original_estimate']
                listRows.append(row)

    df = pd.DataFrame(listRows)
    df = df.groupby(["project", "sprint", "assignee"])[
        "original_estimate"].agg(sum="sum").reset_index()

    dfSuma = np.round(df['sum'],
                      decimals=2)
    df.drop(['sum'], axis='columns', inplace=True)
    df = df.assign(sum=dfSuma)

    df = df.sort_values('assignee', ascending=True)
    # df.to_csv("dfAssignee.csv", index=False)
    # print("dfAssignee.csv creado correctamente")
    return df
