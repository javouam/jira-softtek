from tracemalloc import start
import numpy as np
import pandas as pd
import streamlit as st
import HistogramaVelocidadSprint
import HistogramaStack
import EficienciaPromedio
import PieChart
import DataFrame


def craeteSideBar():
    projectKey = st.sidebar.text_input('Project Key')
    if projectKey != "":
        dfInfoJira, listSprintsStates = DataFrame.createDfByInfoJira(
            projectKey)

        # if dfInfoJira.empty != True:
        st.sidebar.header("Filtros")
        opt = dfInfoJira["Board_name"].unique()
        board = st.sidebar.selectbox(
            "Seleccione un Board:", opt, index=0)
        if len(board) > 0:
            df_board = dfInfoJira.query("Board_name==@board")
            optSprint = df_board["Sprint_name"].unique()
            sprint = st.sidebar.selectbox("Seleccione un Sprint:",
                                          optSprint, index=len(optSprint)-1)
            df_sprint = dfInfoJira.query("Sprint_name==@sprint")
            createMainpage(df_sprint, projectKey, board,
                           sprint, listSprintsStates)
        # else:
            # st.header("No hay Historias de Usuario en el proyecto")  
###############################################################################################################


def createMainpage(df_sprint, projectKey, boardName, sprint, listSprintsStates):
    st.title(":bar_chart: Tablero Agil para el proyecto "+projectKey)
    (dfAllIssues, setSprints) = DataFrame.createDfAllIssuesByProject(projectKey)

    if dfAllIssues.empty != True:
        dfSprintsUSP = DataFrame.createDfSprintsUSP(
            dfAllIssues, setSprints, listSprintsStates)
        stories_by_sprint = DataFrame.createDfStoriesBySprint(df_sprint)

    df_all_bugs, bugs_by_sprint = DataFrame.createDfBugs(projectKey)

    dataRows, dataSprints = DataFrame.getInfoIssuesIntoSprints(
        projectKey, boardName)

    ############################################################
    st.info("Información general del proyecto")

    # Velocidad promedio (Story points por Sprint)
    if dfAllIssues.empty != True:
        chart1 = HistogramaVelocidadSprint.createChart(dfSprintsUSP)
        st.plotly_chart(chart1, use_container_width=True)
    else:
        st.text(
            "No hay Historias de Usuario en el proyecto para mostrar el Histograma de Velocidad")

    lef_column3, right_column3 = st.columns(2)
    if isinstance(df_all_bugs, str):
        st.text(df_all_bugs)
    else:
        dfDefectType = DataFrame.createDfBugsDefectType(
            df_all_bugs, "Defect_Type")
        dfDetectionPhase = DataFrame.createDfBugsDefectType(
            df_all_bugs, "Detection_Phase")
        dfInjectionPhase = DataFrame.createDfBugsDefectType(
            df_all_bugs, "Injection_Phase")

        # Histograma de errores por sprint
        chart5 = HistogramaStack.createChart(bugs_by_sprint, "errores")
        st.plotly_chart(chart5, use_container_width=True)

        lef_column2, right_column2 = st.columns(2)
        # Tipos de Defectos encontrados en el proyecto
        chart6 = PieChart.createChart(dfDefectType, "Defect_Type")
        lef_column2.plotly_chart(chart6, use_container_width=True)
        # Fases de deteccción de defectos
        chart7 = PieChart.createChart(dfDetectionPhase, "Detection_Phase")
        right_column2.plotly_chart(chart7, use_container_width=True)

        # Fases de inyección de defectos
        chart8 = PieChart.createChart(dfInjectionPhase, "Injection_Phase")
        lef_column3.plotly_chart(chart8, use_container_width=True)

    if dfAllIssues.empty != True:
        # % Eficiencia promedio
        chart2 = EficienciaPromedio.createChart(
            dfSprintsUSP, "all", "null")
        right_column3.plotly_chart(chart2, use_container_width=True)

    df_assignee = DataFrame.createDfAssignee(dataRows)
    chart9 = HistogramaStack.createChart(df_assignee, "assignee")
    st.plotly_chart(chart9, use_container_width=True)

    ############################################################
    st.info("Información por Sprint")
    if dfAllIssues.empty != True:
        lef_column4, right_column4 = st.columns(2)
        # Avance del Sprint (chart Pie)
        chart4 = PieChart.createChart(stories_by_sprint, "Avance_del_sprint")
        lef_column4.plotly_chart(chart4, use_container_width=True)
        # % Eficiencia promedio por Sprint
        chart3 = EficienciaPromedio.createChart(dfSprintsUSP, "sprint", sprint)
        right_column4.plotly_chart(chart3, use_container_width=True)
        st.write("Estatus por Sprint")
        st.write(stories_by_sprint)
    else:
        st.text(
            "No hay Historias de Usuario en el proyecto para mostrar las gráficas correspondientes")
    ############################################################

    st.info("Información de todos los Issues en el proyecto")    
    allIssueTypesAllSprints=DataFrame.createDfAllIssuesTypesByProject(projectKey)
    csv_to_download = allIssueTypesAllSprints.to_csv().encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv_to_download,
        file_name='AllIssueTypes.csv',
        mime='text/csv',
    )
    st.write(allIssueTypesAllSprints)

    ############################################################
    # st.info("Información de SubTasks de Historias/Tareas asignadas a los Sprints")
    # df_tasks, columnsFormat_tasks = DataFrame.createInfoTasksByIssueIntoSprints(
    #     dataRows)
    # csv_to_download = df_tasks.to_csv().encode('utf-8')
    # st.download_button(
    #     label="Download data as CSV",
    #     data=csv_to_download,
    #     file_name='WorklogsAllIssues.csv',
    #     mime='text/csv',
    # )
    # st.write(df_tasks.style.format(columnsFormat_tasks))

    # st.info("Información de Historias/Tareas vs. Sprints")
    # col1, col2, col3, col4 = st.columns(4)
    # with col1:
    #     color1 = st.color_picker('Historias', '#76D7C4', key=1)
    # with col2:
    #     color2 = st.color_picker('Subtasks de Historias', '#A1F9C3', key=2)
    # with col3:
    #     color3 = st.color_picker('Tareas', '#7AA6EA', key=3)
    # with col4:
    #     color4 = st.color_picker('Subtasks de Tareas', '#85C1E9', key=4)

    # df_stories, columnsFormat_stories = DataFrame.createInfoBySprint(
    #     dataRows, dataSprints)
    # st.write(df_stories.format(columnsFormat_stories))

    # st.info("Información por persona")
    # df_PerUser, columnsFormat_perUser = DataFrame.createDfTimePerUser(
    #     listSprintsStates, dataRows)
    # st.write(df_PerUser.style.format(columnsFormat_perUser))


###########################################################################################################
st.set_page_config(page_title="Agile Dashboard",
                   page_icon=":bar_chart:",
                   layout="wide")
style = """
        <style>
            footer {visibility: hidden;}
        </style>
"""
st.markdown(style, unsafe_allow_html=True)
craeteSideBar()
