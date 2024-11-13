from typing import Tuple, List, Union, Any
import dash
from dash import dcc, html, dash_table, Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import base64
import io
from services.data_tools import generate_missing_data_matrix_from, remove_nan_rows_from


class Dashboard:
    def __init__(self) -> None:
        self.app: dash.Dash = dash.Dash(__name__)
        self.dataframe: pd.DataFrame = pd.DataFrame()
        self.layout()

    def layout(self) -> None:
        self.app.layout = html.Div(
            [
                # Header
                html.Div(
                    [
                        html.H1(
                            "Visualizador de Dados Multidimensionais",
                            className="text-center mb-4",
                        ),
                    ],
                    style={
                        "padding": "20px",
                        "background": "#f8f9fa",
                        "borderBottom": "1px solid #dee2e6",
                    },
                ),
                # Main Content Area
                html.Div(
                    [
                        # Sidebar com Controles
                        html.Div(
                            [
                                # Upload Section
                                html.Div(
                                    [
                                        html.H3("Carregar Dados"),
                                        dcc.Upload(
                                            id="upload-data",
                                            children=html.Div(
                                                ["selecione um arquivo CSV"]
                                            ),
                                            style={
                                                "width": "100%",
                                                "height": "60px",
                                                "lineHeight": "60px",
                                                "borderWidth": "2px",
                                                "borderStyle": "dashed",
                                                "borderRadius": "5px",
                                                "textAlign": "center",
                                                "margin": "10px 0",
                                            },
                                            multiple=False,
                                        ),
                                    ],
                                    className="mb-4",
                                ),
                                # Data Manipulation
                                html.Div(
                                    [
                                        html.H3("Manipulação de Dados"),
                                        html.Div(
                                            [
                                                html.Button(
                                                    "Remover Dados Ausentes",
                                                    id="remove-missing-data-button",
                                                    className="button-primary mb-2",
                                                    style={"width": "100%"},
                                                ),
                                                html.Button(
                                                    "Normalização",
                                                    id="normalize-button",
                                                    className="button-primary mb-2",
                                                    style={"width": "100%"},
                                                ),
                                                html.Button(
                                                    "Gerar Visualização",
                                                    id="visualize-graph-button",
                                                    className="button-primary",
                                                    style={"width": "100%"},
                                                ),
                                            ]
                                        ),
                                        html.Div(id="output-data-normalized"),
                                    ]
                                ),
                            ],
                            style={
                                "width": "250px",
                                "padding": "20px",
                                "background": "#f8f9fa",
                                "borderRight": "1px solid #dee2e6",
                                "height": "calc(100vh - 100px)",
                                "overflowY": "auto",
                            },
                        ),
                        # Main Visualization Area
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H2("Gráfico de Coordenadas Paralelas"),
                                        dcc.Graph(
                                            id="parallel-coordinates-plot",
                                            style={"height": "calc(100vh - 400px)"},
                                        ),
                                    ]
                                ),
                                # Exploration Area
                                html.Div(
                                    [
                                        dcc.Tabs(
                                            [
                                                dcc.Tab(
                                                    label="Dados",
                                                    children=[
                                                        html.Div(
                                                            id="output-data-upload"
                                                        )
                                                    ],
                                                ),
                                                dcc.Tab(
                                                    label="Dados Ausentes",
                                                    children=[
                                                        dcc.Graph(
                                                            id="missing-data-matrix"
                                                        )
                                                    ],
                                                ),
                                                dcc.Tab(
                                                    label="Estatísticas",
                                                    children=[
                                                        html.Div(
                                                            id="statistics-content"
                                                        )
                                                    ],
                                                ),
                                            ]
                                        )
                                    ],
                                    style={
                                        "marginTop": "20px",
                                        "height": "200px",
                                        "overflowY": "auto",
                                    },
                                ),
                            ],
                            style={"flex": "1", "padding": "20px", "overflowY": "auto"},
                        ),
                    ],
                    style={"display": "flex", "height": "calc(100vh - 100px)"},
                ),
            ]
        )

    def setup_callbacks(self) -> None:
        @self.app.callback(
            Output('output-data-upload', 'children'),  
            Output('missing-data-matrix', 'figure'),   
            Input('upload-data', 'contents'),
            Input('remove-missing-data-button', 'n_clicks'),
            State('output-data-upload', 'children')     
        )
        def update_data(contents, n_clicks, data):
            if contents is not None:
                # Carregar dados do CSV
                _, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)                
                try:
                    self.dataframe = pd.read_csv(io.StringIO(decoded.decode('utf-8')))   
                    # Gera a matriz de dados ausentes
                    missing_data_matrix = generate_missing_data_matrix_from(self.dataframe)
                    # Retorna a tabela e a matriz
                    return (
                        dash_table.DataTable(
                            data=self.dataframe.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in self.dataframe.columns],
                            page_size=10,
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'textAlign': 'left',
                                'padding': '5px',
                            },
                            style_header={
                                'backgroundColor': 'lightgrey',
                                'fontWeight': 'bold'
                            }
                        ),
                        {
                            'data': [],
                            'layout': go.Layout(
                                images=[dict(
                                    source=missing_data_matrix,
                                    x=0,
                                    y=1,
                                    xref="paper",
                                    yref="paper",
                                    sizex=1,
                                    sizey=1,
                                    xanchor="left",
                                    yanchor="top",
                                    opacity=1,
                                    layer="above"
                                )],
                                width=700,
                                height=500,
                                margin=dict(l=0, r=0, t=0, b=0),
                                hovermode='closest'
                            )
                        }
                    )
                except Exception as e:
                    return f"Erro ao carregar o arquivo: {str(e)}", go.Figure() 

            if n_clicks > 0:  
                if self.dataframe.empty:
                    return dash_table.DataTable(), go.Figure()                  
                # Removing NaN
                self.dataframe = remove_nan_rows_from(self.dataframe)
                # Gera a nova matriz de dados ausentes
                missing_data_matrix = generate_missing_data_matrix_from(self.dataframe)

                # Atualiza a tabela de dados com o DataFrame tratado
                return (
                    dash_table.DataTable(
                        data=self.dataframe.to_dict('records'),
                        columns=[{"name": i, "id": i} for i in self.dataframe.columns],
                        page_size=10,
                        style_table={'overflowX': 'auto'},
                        style_cell={
                            'textAlign': 'left',
                            'padding': '5px',
                        },
                        style_header={
                            'backgroundColor': 'lightgrey',
                            'fontWeight': 'bold'
                        }
                    ),
                    {
                        'data': [],
                        'layout': go.Layout(
                            images=[dict(
                                source=missing_data_matrix,
                                x=0,
                                y=1,
                                xref="paper",
                                yref="paper",
                                sizex=1,
                                sizey=1,
                                xanchor="left",
                                yanchor="top",
                                opacity=1,
                                layer="above"
                            )],
                            width=700,
                            height=500,
                            margin=dict(l=0, r=0, t=0, b=0),
                            hovermode='closest'
                        )
                    }
                )

            raise dash.exceptions.PreventUpdate  # Não atualiza se não houver cliques ou uploads válidos
        
    def run(self) -> None:
        self.setup_callbacks()
        self.app.run_server(debug=True)
