import dash
from dash import dcc, html
import plotly.graph_objects as go
from core.patterns.stats_manager import get_stats
import asyncio

dash_app = dash.Dash(
    name='Learning Api Stats',
    requests_pathname_prefix='/stats/'
)

dash_app.title = 'Learning Api Stats'


def get_stats_sync():
    """Синхронна обгортка для async get_stats() та report()"""

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Отримуємо stats manager
        stats = loop.run_until_complete(get_stats())

        # Отримуємо report
        if stats is not None:
            report = loop.run_until_complete(stats.report())
        else:
            report = {
                'lessons_created': 0,
                'resources_created': 0,
                'courses_built': 0,
                'lessons_cloned': 0,
                'registered_users': 0
            }

        loop.close()
        return report
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'lessons_created': 0,
            'resources_created': 0,
            'courses_built': 0,
            'lessons_cloned': 0,
            'registered_users': 0
        }


def serve_layout():
    report = get_stats_sync()

    fig = go.Figure(
        data=[go.Bar(
            x=list(report.keys()),
            y=list(report.values()),
            text=list(report.values()),
            textposition="outside",
            marker_color='lightblue'
        )]
    )
    fig.update_layout(
        title="Learning API Statistics",
        xaxis_title="Entity",
        yaxis_title="Count",
        template="plotly_white"
    )

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
        ], style={'margin': '20px'}),
        dcc.Interval(
            id='interval-component',
            interval=5 * 1000,
            n_intervals=0
        )
    ])


dash_app.layout = serve_layout