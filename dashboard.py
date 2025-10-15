# dashboard.py
import glob
import os
import pandas as pd
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

def latest_report():
    files = sorted(glob.glob("reports/test_results_*.csv"))
    if not files:
        return None
    return files[-1]


def list_reports():
    files = sorted(glob.glob("reports/test_results_*.csv"))
    # return reversed so newest first in dropdown
    return list(reversed(files))

def build_app():
    # Use a Bootstrap theme for a clean, responsive layout
    app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
    report = latest_report()

    # Build initial layout with dropdown and placeholders. Content will be filled by callbacks.
    reports = list_reports()
    options = [{'label': r.split('reports' + os.sep)[-1] if 'reports' in r else r, 'value': r} for r in reports]

    header = dbc.Row([
        dbc.Col(html.H2("VDATS Dashboard"), md=6),
        dbc.Col(html.Div([
            dbc.Label("Select report", html_for='report-dropdown', className='mb-0', style={'marginBottom':'4px'}),
            dcc.Dropdown(id='report-dropdown', options=options, value=reports[0] if reports else None, clearable=False)
        ], style={'textAlign': 'right'}), md=6)
    ], align='center', className='my-2')

    # KPI cards placeholders
    def kpi_card(title, id_value, icon, color='dark'):
        return dbc.Card(
            dbc.CardBody([
                html.Div(icon, style={'fontSize':'20px'}),
                html.H6(title, className='card-title'),
                html.H3(id=id_value, className='card-text')
            ]), className='text-center'
        )

    kpis = dbc.Row([
        dbc.Col(kpi_card('Total', 'kpi-total', '📊'), md=3),
        dbc.Col(kpi_card('Pass Rate', 'kpi-pass-rate', '✅'), md=3),
        dbc.Col(kpi_card('Passed', 'kpi-passed', '🟣'), md=3),
        dbc.Col(kpi_card('Failed', 'kpi-failed', '🔴'), md=3),
    ], className='mb-3')

    graphs = dbc.Row([
        dbc.Col(dcc.Graph(id='status-graph', figure={}), md=4),
        dbc.Col(dcc.Graph(id='reading-graph', figure={}), md=8),
    ])

    # DataTable for recent rows
    table = dbc.Row(dbc.Col(dash_table.DataTable(id='results-table', page_size=10,
                                                 style_table={'overflowX': 'auto'},
                                                 sort_action='native',
                                                 filter_action='native'), md=12))

    footer = dbc.Row(dbc.Col(html.Div(id='last-ts', className='text-muted mt-2')))

    content = dbc.Container([header, kpis, graphs, table, footer], fluid=True)

    app.layout = content

    # Callbacks to populate KPIs, charts and table when report changes
    @app.callback(
        [Output('kpi-total', 'children'),
         Output('kpi-pass-rate', 'children'),
         Output('kpi-passed', 'children'),
         Output('kpi-failed', 'children'),
         Output('status-graph', 'figure'),
         Output('reading-graph', 'figure'),
         Output('results-table', 'data'),
         Output('results-table', 'columns'),
         Output('last-ts', 'children')],
        [Input('report-dropdown', 'value')]
    )
    def update_dashboard(selected_report):
        if not selected_report:
            return ['0', '0%', '0', '0', {}, {}, [], [], 'No report selected']

        try:
            df = pd.read_csv(selected_report)
        except Exception:
            return ['0', '0%', '0', '0', {}, {}, [], [], 'Failed to load report']

        total = len(df)
        passed = int((df['status'] == 'PASS').sum()) if 'status' in df.columns else 0
        failed = int((df['status'] == 'FAIL').sum()) if 'status' in df.columns else 0
        pass_rate = f"{(100 * passed / total):.1f}%" if total else '0%'

        # Status pie
        if 'status' in df.columns:
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            fig_status = px.pie(status_counts, names='status', values='count',
                                color='status', color_discrete_map={"PASS":"#6a0dad","FAIL":"#d62828"},
                                title='Status Distribution', template='plotly_white')
        else:
            fig_status = {}

        # Readings scatter (coerce to numeric)
        df['reading'] = pd.to_numeric(df.get('reading', pd.Series()), errors='coerce')
        fig_reading = px.scatter(df, x='test_id', y='reading', color=df.get('status'),
                                 color_discrete_map={"PASS":"#6a0dad","FAIL":"#d62828"},
                                 title='Readings by Test ID', template='plotly_white', hover_data=['timestamp_utc'])

        # DataTable
        columns = [{'name': c, 'id': c} for c in df.columns]
        data = df.to_dict('records')

        last_ts = df['timestamp_utc'].max() if 'timestamp_utc' in df.columns else selected_report

        return [str(total), pass_rate, str(passed), str(failed), fig_status, fig_reading, data, columns, f"Last timestamp: {last_ts}"]

    return app

if __name__ == "__main__":
    app = build_app()
    app.run(debug=True, host="0.0.0.0", port=8050)