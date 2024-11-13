from typing import Tuple, List, Union, Any
import dash
from dash import dcc, html, dash_table, Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import base64
import io


class Dashboard:
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.dataframe = pd.DataFrame()
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
                                                [
                                                    "Arraste e solte ou ",
                                                    html.A("selecione um arquivo CSV"),
                                                ]
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
                                # Controles de Dimensões
                                html.Div(
                                    [
                                        html.H3("Dimensões"),
                                        html.Div(id="dimension-checklist"),
                                    ],
                                    className="mb-4",
                                ),
                                # Controles de Manipulação
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
                                # Área de Análise Exploratória
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
            [
                Output("output-data-upload", "children"),
                Output("missing-data-matrix", "figure"),
            ],
            [Input("upload-data", "contents")],
            [State("upload-data", "filename")],
        )
        def update_output(contents: Union[str, None], filename: str) -> Union[
            Tuple[List[html.Div], Any],
            Tuple[dash_table.DataTable, go.Figure],
        ]:
            if contents is None:
                return [html.Div(["Nenhum arquivo carregado."])], dash.no_update

            content_string: str = ""
            _, content_string = contents.split(",")
            decoded: bytes = base64.b64decode(content_string)
            try:
                if "csv" in filename:
                    self.dataframe = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
                else:
                    return [
                        html.Div(["Arquivo não suportado: ", filename])
                    ], dash.no_update
            except Exception as e:
                return [
                    html.Div(["Erro ao processar o arquivo: ", str(e)])
                ], dash.no_update

            table = dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in self.dataframe.columns],
                data=self.dataframe.to_dict("records"),
                page_size=10,
                style_table={"overflowX": "auto"},
            )

            missing_data_matrix_fig = ff.create_annotated_heatmap(
                z=self.dataframe.isna().astype(int).values,
                x=list(self.dataframe.columns),
                y=list(self.dataframe.index),
                annotation_text=self.dataframe.isna().astype(int).astype(str).values,
                colorscale="Viridis",
            )

            return table, missing_data_matrix_fig

        @self.app.callback(
            Output("dimension-checklist", "children"),
            [Input("upload-data", "contents")],
        )
        def update_dimensions_checklist(contents):
            if contents is None or self.dataframe.empty:
                return []

            numeric_cols = self.dataframe.select_dtypes(include=[float, int]).columns
            return dcc.Checklist(
                options=[{"label": f" {col}", "value": col} for col in numeric_cols],
                value=list(numeric_cols),
                id="dimension-selector",
                style={"marginLeft": "10px"},
            )

        @self.app.callback(
            Output("statistics-content", "children"), [Input("upload-data", "contents")]
        )
        def update_statistics(contents):
            if contents is None or self.dataframe.empty:
                return html.Div("Carregue um dataset para ver as estatísticas")

            stats = self.dataframe.describe()
            return dash_table.DataTable(
                data=stats.reset_index().to_dict("records"),
                columns=[
                    {"name": col, "id": col} for col in stats.reset_index().columns
                ],
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left", "padding": "5px"},
                style_header={
                    "backgroundColor": "rgb(230, 230, 230)",
                    "fontWeight": "bold",
                },
            )

        @self.app.callback(
            Output("parallel-coordinates-plot", "figure"),
            [Input("dimension-selector", "value"), Input("upload-data", "contents")],
        )
        def update_parallel_coordinates(selected_dimensions, contents):
            if contents is None or self.dataframe.empty or not selected_dimensions:
                return {}

            try:
                color_column = selected_dimensions[0]
                fig = px.parallel_coordinates(
                    self.dataframe,
                    dimensions=selected_dimensions,
                    color=self.dataframe[color_column],
                    color_continuous_scale=px.colors.sequential.Viridis,
                    labels={color_column: color_column},
                )
                return fig
            except Exception as e:
                print(f"Erro ao atualizar o gráfico: {e}")
                return {}

        @self.app.callback(
            Output("output-data-normalized", "children"),
            [Input("normalize-button", "n_clicks")],
            [State("dimension-selector", "value")],
        )
        def normalize_data(n_clicks, selected_dimensions):
            if n_clicks is None or n_clicks == 0 or not selected_dimensions:
                return ""

            for col in selected_dimensions:
                if col in self.dataframe.columns:
                    self.dataframe[col] = (
                        self.dataframe[col] - self.dataframe[col].min()
                    ) / (self.dataframe[col].max() - self.dataframe[col].min())

            return "Dados normalizados com sucesso!"

    def run(self) -> None:
        self.setup_callbacks()
        self.app.run_server(debug=True)
