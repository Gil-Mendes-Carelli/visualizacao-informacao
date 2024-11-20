from typing import Tuple, List, Union, Any
import dash
from dash import dcc, html, dash_table, Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import base64
import io
from services.data_tools import (
    generate_missing_data_matrix_from,
    remove_nan_rows_from,
    remove_object_columns_from,
)


class Dashboard:
    def __init__(self) -> None:
        self.app: dash.Dash = dash.Dash(__name__)
        self.dataframe: pd.DataFrame = pd.DataFrame()
        self.label_column: str = ''
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
                                        dcc.Store(id="dataset-state", data=None),
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
                                                    "Escolher coluna rótulo",
                                                    id="label-button",
                                                    className="button-primary mb-2",
                                                    style={"width": "100%"},
                                                ),
                                                dcc.Store(id="modal-state", data=False),
                                                dcc.Store(id="selected-label", data=""),
                                                html.Div(
                                                    id="popup-modal",
                                                    children=[
                                                        html.Div(
                                                            [
                                                                html.H3(
                                                                    "Escolher coluna rótulo"
                                                                ),
                                                                dcc.Dropdown(
                                                                    id="dropdown-options",                                                                   
                                                                    placeholder="Selecione uma opção",
                                                                    options = [],
                                                                ),
                                                                html.Button(
                                                                    "Salvar",
                                                                    id="save-modal-button",
                                                                    n_clicks=0,
                                                                ),
                                                                html.Button(
                                                                    "Fechar",
                                                                    id="close-modal-button",
                                                                    n_clicks=0,
                                                                ),
                                                            ],
                                                            style={
                                                                "border": "line",
                                                                "padding": "30px",
                                                                "textAlign": "center",
                                                            },
                                                        ),
                                                    ],
                                                    style={
                                                        "display": "none",  # Inicialmente oculto
                                                        "position": "fixed",
                                                        "top": "50%",
                                                        "left": "50%",
                                                        "transform": "translate(-50%, -50%)",
                                                        "backgroundColor": "white",
                                                        "padding": "20px",
                                                        "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                                                        "zIndex": 1000,
                                                    },
                                                ),
                                                html.Div(
                                                    id="popup-overlay",
                                                    style={
                                                        "display": "none",  # Inicialmente invisível
                                                        "position": "fixed",
                                                        "top": 0,
                                                        "left": 0,
                                                        "width": "100%",
                                                        "height": "100%",
                                                        "backgroundColor": "rgba(0, 0, 0, 0.5)",
                                                        "zIndex": 999,
                                                    },
                                                ),
                                                html.Button(
                                                    "Escolher Dimensões",
                                                    id="dimension-button",
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
            Output("output-data-upload", "children"),
            Output("missing-data-matrix", "figure"),
            Input("upload-data", "contents"),
            Input("remove-missing-data-button", "n_clicks"),
            State("output-data-upload", "children"),
            prevent_initial_call=True,
        )
        def update_data(encoded_dataset, n_clicks, _):
            # print("Callback disparado")

            # Identificar qual input disparou o callback
            ctx = dash.callback_context
            if not ctx.triggered:
                raise dash.exceptions.PreventUpdate

            triggered_input = ctx.triggered[0]["prop_id"].split(".")[0]

            # Caso o input seja o upload de um arquivo
            if triggered_input == "upload-data":
                # print("Arquivo carregado")
                try:
                    _, content_string = encoded_dataset.split(",")
                    decoded = base64.b64decode(content_string)
                    self.dataframe = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
                    missing_data_matrix = generate_missing_data_matrix_from(
                        self.dataframe
                    )
                    return (
                        dash_table.DataTable(
                            data=self.dataframe.to_dict("records"),
                            columns=[
                                {"name": i, "id": i} for i in self.dataframe.columns
                            ],
                            page_size=10,
                            style_table={"overflowX": "auto"},
                            style_cell={"textAlign": "left", "padding": "5px"},
                            style_header={
                                "backgroundColor": "lightgrey",
                                "fontWeight": "bold",
                            },
                        ),
                        {
                            "data": [],
                            "layout": go.Layout(
                                images=[
                                    dict(
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
                                        layer="above",
                                    )
                                ],
                                width=700,
                                height=500,
                                margin=dict(l=0, r=0, t=0, b=0),
                                hovermode="closest",
                            ),
                        },
                    )
                except Exception as e:
                    print(f"Erro: {e}")
                    return "Erro ao carregar arquivo.", go.Figure()

            # Caso o input seja o botão para remover dados ausentes
            if triggered_input == "remove-missing-data-button" and n_clicks > 0:
                print("Botão remover dados ausentes clicado")
                if self.dataframe.empty:
                    return dash_table.DataTable(), go.Figure()
                self.dataframe = remove_nan_rows_from(self.dataframe)
                missing_data_matrix = generate_missing_data_matrix_from(self.dataframe)
                return (
                    dash_table.DataTable(
                        data=self.dataframe.to_dict("records"),
                        columns=[{"name": i, "id": i} for i in self.dataframe.columns],
                        page_size=10,
                        style_table={"overflowX": "auto"},
                        style_cell={"textAlign": "left", "padding": "5px"},
                        style_header={
                            "backgroundColor": "lightgrey",
                            "fontWeight": "bold",
                        },
                    ),
                    {
                        "data": [],
                        "layout": go.Layout(
                            images=[
                                dict(
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
                                    layer="above",
                                )
                            ],
                            width=700,
                            height=500,
                            margin=dict(l=0, r=0, t=0, b=0),
                            hovermode="closest",
                        ),
                    },
                )      
                
            raise dash.exceptions.PreventUpdate
        
        # Callback para abrir, fechar o modal e salvar a seleção do usuário
        @self.app.callback(
            [Output("popup-modal", "style"),
            Output("popup-overlay", "style"),
            Output("modal-state", "data"),
            Output("dropdown-options", "options")],
            [Input("label-button", "n_clicks"),
            Input("close-modal-button", "n_clicks"),
            Input("save-modal-button", "n_clicks")],
            [State("dropdown-options", "value"),
            State("modal-state", "data")]
        )
        def modal_interaction(n_clicks_open, n_clicks_close, n_clicks_save, selected_value, modal_state):
            ctx = dash.callback_context  # Objeto do contexto atual do callback
            triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

            # Abrir o modal
            if triggered_id == "label-button":
                # Carregar as opções do dataframe
                options = [{'label': label, 'value': label} for label in self.dataframe.select_dtypes(include="object").columns.to_list()]
                return {
                    "display": "block",  # Mostrar o modal
                    "position": "fixed",
                    "top": "50%",
                    "left": "50%",
                    "transform": "translate(-50%, -50%)",
                    "backgroundColor": "white",
                    "padding": "20px",
                    "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                    "zIndex": 1000,
                }, {
                    "display": "block",  # Mostrar o overlay
                    "position": "fixed",
                    "top": 0,
                    "left": 0,
                    "width": "100%",
                    "height": "100%",
                    "backgroundColor": "rgba(0, 0, 0, 0.5)",
                    "zIndex": 999,
                }, True, options  # Passar as opções para o Dropdown

            # Fechar o modal
            if triggered_id == "close-modal-button":
                return {
                    "display": "none",  # Ocultar o modal
                }, {
                    "display": "none",  # Ocultar o overlay
                }, False, dash.no_update  # Não mudar as opções do dropdown

            # Salvar a seleção do usuário e fechar o modal
            if triggered_id == "save-modal-button":
                if selected_value:
                    self.label_column = selected_value  # Salvar a escolha do usuário
                    print(f"Escolha do usuário: {self.label_column}")
                    self.dataframe = remove_object_columns_from(self.dataframe, self.label_column)                    
                    # Fechar o modal após salvar
                    return {
                        "display": "none",  # Ocultar o modal
                    }, {
                        "display": "none",  # Ocultar o overlay
                    }, False, dash.no_update  # Não mudar a seleção do dropdown
                else:
                    # Se não houver seleção, apenas retornar o modal aberto
                    print("Selecione uma opção antes de salvar!")
                    return dash.no_update, dash.no_update, modal_state, dash.no_update

            # Se nenhum clique ocorreu, não mudar nada
            return dash.no_update, dash.no_update, modal_state, dash.no_update

        
        
        # # Callback para abrir, fechar o modal e salvar a seleção do usuário
        # @self.app.callback(
        #     [Output("popup-modal", "style"),
        #     Output("popup-overlay", "style"),
        #     Output("modal-state", "data"),
        #     Output("dropdown-options", "options")],
        #     [Input("label-button", "n_clicks"),
        #     Input("close-modal-button", "n_clicks"),
        #     Input("save-modal-button", "n_clicks")],
        #     [State("dropdown-options", "value"),
        #     State("modal-state", "data")]
        # )
        # def modal_interaction(n_clicks_open, n_clicks_close, n_clicks_save, selected_value, modal_state):
        #     # Abrir o modal
        #     if n_clicks_open and n_clicks_open > 0:
        #         print('botão rótulo')
        #         # Carregar as opções do dataframe
        #         options = [{'label': label, 'value': label} for label in self.dataframe.select_dtypes(include="object").columns.to_list()]
        #         return {
        #             "display": "block",  # Mostrar o modal
        #             "position": "fixed",
        #             "top": "50%",
        #             "left": "50%",
        #             "transform": "translate(-50%, -50%)",
        #             "backgroundColor": "white",
        #             "padding": "20px",
        #             "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
        #             "zIndex": 1000,
        #         }, {
        #             "display": "block",  # Mostrar o overlay
        #             "position": "fixed",
        #             "top": 0,
        #             "left": 0,
        #             "width": "100%",
        #             "height": "100%",
        #             "backgroundColor": "rgba(0, 0, 0, 0.5)",
        #             "zIndex": 999,
        #         }, True, options  # Passar as opções para o Dropdown

        #     # Fechar o modal
        #     if n_clicks_close and n_clicks_close > 0:
        #         return {
        #             "display": "none",  # Ocultar o modal
        #         }, {
        #             "display": "none",  # Ocultar o overlay
        #         }, False, dash.no_update  # Não mudar as opções do dropdown

        #     # Salvar a seleção do usuário e fechar o modal
        #     if n_clicks_save and n_clicks_save > 0:
        #         if selected_value:
        #             self.label_column = selected_value  # Salvar a escolha do usuário
        #             print(f"Escolha do usuário: {self.label_column}")
                    
        #             # Fechar o modal após salvar
        #             return {
        #                 "display": "none",  # Ocultar o modal
        #             }, {
        #                 "display": "none",  # Ocultar o overlay
        #             }, False, dash.no_update  # Não mudar a seleção do dropdown
        #         else:
        #             # Se não houver seleção, apenas retornar o modal aberto
        #             print("Selecione uma opção antes de salvar!")
        #             return dash.no_update, dash.no_update, modal_state, dash.no_update

        #     # Se nenhum clique ocorreu, não mudar nada
        #     return dash.no_update, dash.no_update, modal_state, dash.no_update


        # # Callback para abrir o modal e carregar as opções do dropdown
        # @self.app.callback(
        #     [Output("popup-modal", "style"),
        #     Output("popup-overlay", "style"),
        #     Output("modal-state", "data"),
        #     Output("dropdown-options", "options")],
        #     [Input("label-button", "n_clicks")],
        #     [State("modal-state", "data")]
        # )
        # def open_modal(n_clicks, modal_state):
        #     if n_clicks > 0:
        #         # Carregar as opções do dataframe
        #         options = [{'label': label, 'value': label} for label in self.dataframe.select_dtypes(include="object").columns.to_list()]
        #         print(options)
        #         # Exibir o modal
        #         return {
        #             "display": "block",  # Mostrar o modal
        #             "position": "fixed",
        #             "top": "50%",
        #             "left": "50%",
        #             "transform": "translate(-50%, -50%)",
        #             "backgroundColor": "white",
        #             "padding": "20px",
        #             "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
        #             "zIndex": 1000,
        #         }, {
        #             "display": "block",  # Mostrar o overlay
        #             "position": "fixed",
        #             "top": 0,
        #             "left": 0,
        #             "width": "100%",
        #             "height": "100%",
        #             "backgroundColor": "rgba(0, 0, 0, 0.5)",
        #             "zIndex": 999,
        #         }, True, options  # Passar as opções para o Dropdown

        #     return dash.no_update, dash.no_update, modal_state, dash.no_update


        # # Callback para fechar o modal
        # @self.app.callback(
        #     [Output("popup-modal", "style"),
        #     Output("popup-overlay", "style"),
        #     Output("modal-state", "data")],
        #     [Input("close-modal-button", "n_clicks")],
        #     [State("modal-state", "data")]
        # )
        # def close_modal(n_clicks, modal_state):
        #     if n_clicks:
        #         # Ocultar o modal
        #         return {
        #             "display": "none",  # Ocultar o modal
        #         }, {
        #             "display": "none",  # Ocultar o overlay
        #         }, False

        #     return dash.no_update, dash.no_update, modal_state
        
        
    def run(self) -> None:
        self.setup_callbacks()
        self.app.run_server(debug=True)
