import dash
from dash import dcc, html
import plotly.express as px
from core.patterns import stats


dash_app = dash.Dash(
    name='Learning Api Stats',
    requests_pathname_prefix='/stats/'
)

dash_app.title = 'Learning Api Stats'

def serve_layout():
    report = stats.report()
    fig = px.bar(
        x=list(report.keys()),
        y=list(report.values()),
        labels={'x': 'Entity', 'y': 'Count'},
        title='Learning API Statistics',
        color=list(report.keys()),
        text=list(report.values())
    )
    fig.update_traces(textposition='outside')

    return html.Div([
        html.H1('📊 Learning API Dashboard', style={'textAlign': 'center'}),
        dcc.Graph(figure=fig),
        html.Div([
            html.H3('Summary'),
            html.Ul([
                html.Li(f"Lessons created: {report['lessons_created']}"),
                html.Li(f"Resources created: {report['resources_created']}"),
                html.Li(f"Courses built: {report['courses_built']}"),
                html.Li(f"Lessons cloned: {report['lessons_cloned']}"),
            ])
        ], style={'margin': '20px'})
    ])

dash_app.layout = serve_layout