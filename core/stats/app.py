import dash
from dash import dcc, html
import plotly.graph_objects as go
from core.patterns import stats


dash_app = dash.Dash(
    name='Learning Api Stats',
    requests_pathname_prefix='/stats/'
)

dash_app.title = 'Learning Api Stats'

def serve_layout():
    report = stats.report()
    fig = go.Figure(
        data=[go.Bar(
            x=list(report.keys()),
            y=list(report.values()),
            text=list(report.values()),
            textposition="outside"
        )]
    )
    fig.update_layout(title="Learning API Statistics", xaxis_title="Entity", yaxis_title="Count")

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
                html.Li(f"Registered users: {report['registered_users']}")
            ])
        ], style={'margin': '20px'})
    ])

dash_app.layout = serve_layout