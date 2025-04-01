import plotly.express as px


def createChart(df, type):
    if type == "errores":
        df = df.rename(columns={'count': 'Cantidad', 'Sprint_Name': ' '})
        fig = px.bar(df, x=" ", y="Cantidad", text="Cantidad",
                     color="Status", title="Histograma de Defectos reportados por Sprint")
        fig.update_traces(textposition='inside', textfont_size=16)
    if type == "assignee":
        df = df.rename(columns={'sum': 'Original_estimate', 'sprint': ' '})
        fig = px.bar(df, x=" ", y="Original_estimate", text="Original_estimate",
                     color="assignee", title="Esfuerzo Planeado por Sprint")
        fig.update_traces(textfont_size=16)
    return fig
