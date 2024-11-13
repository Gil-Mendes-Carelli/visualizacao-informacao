import dash
from dash import dcc, html, dash_table, Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import base64
import io


class Dashboard:
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.dataframe = pd.DataFrame()
        self.setup_layout()

    def setup_layout(self) -> None:
        self.app.layout = html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gridTemplateRows": "1fr 1fr",
                "height": "100vh",
                "gap": "10px",
            },
            children=[
                # left top : Upload and data table
                html.Div(
                    style={
                        "border": "1px solid black",
                        "padding": "10px",
                        "overflow": "auto",
                    },
                    children=[
                        html.H1("Visualizador de Dados Multidimensionais"),
                        dcc.Upload(
                            id="upload-data",
                            children=html.Div(
                                [
                                    "Arraste e solte ou ",
                                    html.A("selecione um arquivo CSV"),
                                ]
                            ),
                            style={
                                "width": "98%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "2px",
                                "borderStyle": "groove",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "margin": "10px",
                            },
                            multiple=False,
                        ),
                        html.Div(id="output-data-upload"),  # data table
                    ],
                ),
                # right top: parallels coordinates map
                html.Div(
                    style={"border": "1px solid black", "padding": "10px"},
                    children=[
                        html.H2("Gráfico de Coordenadas Paralelas"),
                        dcc.Graph(
                            id="parallel-coordinates-plot"
                        ),  # parallels coordinates map
                    ],
                ),
                # left bottom: missing data matrix
                html.Div(
                    style={"border": "1px solid black", "padding": "10px"},
                    children=[
                        html.H2("Matriz de Dados Ausentes"),
                        dcc.Graph(id="missing-data-matrix"),
                    ],
                ),
                # right bottom: data manipulation
                html.Div(
                    style={"border": "1px solid black", "padding": "10px"},
                    children=[
                        html.H2("Manipulação de Dados"),
                        html.Button(
                            "Remover Dados Ausentes",
                            id="remove-missing-data-button",
                            n_clicks=0,
                        ),
                        html.Button(
                            "Filtrar Colunas", id="select-columns-button", n_clicks=0
                        ),
                        html.Button("Normalização", id="normalize-button", n_clicks=0),
                        html.Button(
                            "Gerar Viaualização",
                            id="visualize-graph-button",
                            n_clicks=0,
                        ),
                    ],
                ),
            ],
        )

    def setup_callbacks(self) -> None:
        @self.app.callback(
            [
                Output("output-data-upload", "children"),
                Output("missing-data-matrix", "figure"),
                Output("parallel-coordinates-plot", "figure"),
            ],
            [Input("upload-data", "contents")],
            [State("upload-data", "filename")],
        )
        def update_output(contents, filename):
            if contents is None:
                return (
                    [html.Div(["Nenhum arquivo carregado."])],
                    dash.no_update,
                    dash.no_update,
                )

            content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)
            try:
                if "csv" in filename:
                    self.dataframe = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
                else:
                    return (
                        [html.Div(["Arquivo não suportado: ", filename])],
                        dash.no_update,
                        dash.no_update,
                    )
            except Exception as e:
                return (
                    [html.Div(["Erro ao processar o arquivo: ", str(e)])],
                    dash.no_update,
                    dash.no_update,
                )
            
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

            numeric_cols = self.dataframe.select_dtypes(include=[float, int]).columns
            if not numeric_cols.empty:
                color_column = numeric_cols[0]
                parallel_coordinates_fig = px.parallel_coordinates(
                    self.dataframe,
                    dimensions=numeric_cols,
                    color=self.dataframe[color_column],
                    color_continuous_scale=px.colors.sequential.Viridis,
                    labels={color_column: color_column},
                )
            else:
                parallel_coordinates_fig = px.parallel_coordinates(self.dataframe)

            return table, missing_data_matrix_fig, parallel_coordinates_fig

    def run(self):
        self.setup_callbacks()
        self.app.run_server(debug=True)