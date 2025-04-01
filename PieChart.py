import plotly.express as px


def createChart(df, type):
    if type == "Avance_del_sprint":
        fig = px.pie(df, values='count',
                     names='Issue_Status', title='Avance del Sprint', hole=0.3)

    if type == "Defect_Type":
        fig = px.pie(df, values='count',
                     names='Defect_Type', title='Defect Type', hole=0.3)

    if type == "Detection_Phase":
        fig = px.pie(df, values='count',
                     names='Detection_Phase', title='Detection Phase', hole=0.3)

    if type == "Injection_Phase":
        fig = px.pie(df, values='count',
                     names='Injection_Phase', title='Injection Phase', hole=0.3)

    fig.update_traces(textposition='inside',
                      textinfo='percent+label', textfont_size=14)
    return fig
