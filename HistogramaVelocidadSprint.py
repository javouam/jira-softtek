import plotly.graph_objects as go


def createChart(df):
    df = df.sort_values('Sprint', ascending=True)
    allCommited = df['All Commited Story Points']
    commited = df['Commited Story Points']
    accepted = df['Accepted Story Points']
    remaining = allCommited-commited
    velocity_per_sprint_chart = go.Figure(data=[
        go.Bar(name='Remaining Commited Story Points',
               x=df['Sprint'], y=remaining, text=remaining, marker_color="crimson"),
        go.Bar(name='New Commited Story Points',
               x=df['Sprint'], y=commited, text=commited, marker_color="#511CFB"),
        go.Bar(name='Accepted Story Points',
               x=df['Sprint'], y=accepted, text=accepted, marker_color="#479B55"),
    ])
    velocity_per_sprint_chart.update_layout(
        title='Histograma de la Velocidad por Sprint', barmode='group')
    velocity_per_sprint_chart.update_traces(
        textfont_size=16, textangle=0, cliponaxis=False)
    return velocity_per_sprint_chart
