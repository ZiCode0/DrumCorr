import plotly.express as px
import datetime


def fancy_plot(input_trace):
    """
    Draw fancy interactive time series using plotly library
    :param input_trace: target trace to draw
    """
    y = input_trace.data
    x = [datetime.datetime.fromtimestamp(
        input_trace.stats.starttime.datetime.timestamp() + i)
        for i in input_trace.times('relative').tolist()]
    fig = px.scatter(x=x, y=y)
    fig.write_html('first_figure.html', auto_open=True)
