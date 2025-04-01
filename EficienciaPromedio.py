import plotly.graph_objects as go


def createChart(df, type, sprint):
    title = ""
    if type == "sprint":
        df = df.query("Sprint==@sprint")
        title = "% Eficiencia promedio en ["+sprint+"]"
        df["Efficiency"] = (df["Accepted Story Points"] /
                            df["All Commited Story Points"]) * 100

        kpi_mean_efficiency = (df["Accepted Story Points"].mean(
        ) / df["All Commited Story Points"].mean()) * 100 if df["All Commited Story Points"].mean() != 0 else 0

        print("kpi_mean_efficiency")
    else:
        title = "% Eficiencia promedio en todos los sprints cerrados"
        df_mask = df['State'] == 'closed'
        df = df[df_mask]
        df["Efficiency"] = (df["Accepted Story Points"] /
                            df["Commited Story Points"]) * 100

        kpi_mean_efficiency = (df["Accepted Story Points"].mean(
        ) / df["Commited Story Points"].mean()) * 100

    kpi_mean_efficiency_target = 100

    red_min_value = 0
    red_max_value = 85
    yellow_max_value = 95
    green_max_value = 105
    blue_max_value = 120

    kpi_mean_efficiency_chart = go.Figure(go.Indicator(mode="gauge+number+delta",
                                                       value=kpi_mean_efficiency,
                                                       domain={
                                                           'x': [0, 1], 'y': [0, 1]},
                                                       title={
                                                           'text': title},
                                                       delta={'reference': kpi_mean_efficiency_target, 'increasing': {
                                                           'color': "RebeccaPurple"}},
                                                       gauge={'axis': {'range': [0, blue_max_value]},
                                                              'bar': {'color': "darkblue"},
                                                              'steps': [{'range': [red_min_value, red_max_value], 'color': "red"},
                                                                        {'range': [
                                                                            red_max_value, yellow_max_value], 'color': "yellow"},
                                                                        {'range': [
                                                                            yellow_max_value, green_max_value], 'color': "green"},
                                                                        {'range': [
                                                                            green_max_value, blue_max_value], 'color': "blue"}
                                                                        ]}))
    return kpi_mean_efficiency_chart
