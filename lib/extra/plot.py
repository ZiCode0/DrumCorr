import plotly.express as px
import datetime


def fancy_plot(input_traces):
    """
    Draw fancy interactive time series using plotly library
    :param input_traces: target trace to draw
    """
    if type(input_traces) is list:
        y = [i.data for i in input_traces]  # input_trace.data
    else:
        y = input_traces.data

    x = [datetime.datetime.fromtimestamp(
        input_traces[0].stats.starttime.datetime.timestamp() + i)
        for i in input_traces[0].times('relative').tolist()]

    fig = px.line(x=x, y=y)
    fig.write_html('first_figure.html', auto_open=True)
