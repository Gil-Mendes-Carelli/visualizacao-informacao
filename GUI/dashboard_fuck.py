import dash
from dash import dcc, html, dash_table
import pandas as pd
from dash.dependencies import Input, Output, State
import base64
import io
import missingno as msno
import matplotlib.pyplot as plt
from typing import List, Optional, Tuple
from services.data_tools import generate_missing_data_matrix_from, remove_object_columns_from, load_csv_from


class Dashboard:
    def __init__(self) -> None:
        self.app: dash.Dash = dash.Dash(__name__)
        self.dataframe: pd.DataFrame = None
        
    def load_data(self, contents: str) -> None:
        _, content_string = contents.split(',')
        decoded = io.StringIO(base64.b64decode(content_string).decode('utf-8'))
        self.dataframe = pd.read_csv(decoded)

    # def layout(self) -> html.Div:
    #     """Define o layout do aplicativo Dash."""
    #     return html.Div(
    #         style={"display": "flex", "height": "100vh"},
    #         children=[
    #             # Coluna esquerda para dados e matriz de dados ausentes
    #             html.Div(
    #                 style={"flex": "1", "padding": "20px", "overflow": "auto"},
    #                 children=[
    #                     html.H1("Visualizador de Dados Multidimensionais"),
    #                     dcc.Upload(
    #                         id="upload-data",
    #                         children=html.Div(
    #                             [
    #                                 "Arraste e solte ou ",
    #                                 html.A("selecione um arquivo CSV"),
    #                             ]
    #                         ),
    #                         style={
    #                             "width": "100%",
    #                             "height": "60px",
    #                             "lineHeight": "60px",
    #                             "borderWidth": "1px",
    #                             "borderStyle": "dashed",
    #                             "borderRadius": "5px",
    #                             "textAlign": "center",
    #                             "margin": "10px",
    #                         },
    #                         multiple=False,
    #                     ),
    #                     html.Div(id="output-data-upload"),  # Tabela de dados
    #                     html.H5("Matriz de Dados Ausentes:"),
    #                     html.Img(id="missing-data-matrix", style={"marginTop": "20px"}),
    #                 ],
    #             ),
    #             # Coluna direita (pode ser usada para visualizações futuras)
    #             html.Div(
    #                 style={"flex": "1", "padding": "20px", "overflow": "auto"},
    #                 children=[html.H2("Filtragem de dados")],
    #             ),
    #         ],
    #     )

from dash import Dash, dcc, html, Input, Output
import dash_table
import pandas as pd
from io import StringIO

class Dashboard:
    def __init__(self):
        self.dataframe: pd.DataFrame = pd.DataFrame()

    def load_data(self, contents: str) -> None:
        """Carrega o DataFrame a partir do conteúdo do arquivo CSV."""
        content_type, content_string = contents.split(',')
        decoded = StringIO(base64.b64decode(content_string).decode('utf-8'))
        self.dataframe = pd.read_csv(decoded)
        
    def layout(self) -> html.Div:
        # Exibindo as colunas de tipo objeto no layout
        object_columns: List[str] = self.dataframe.select_dtypes(include="object").columns.to_list()
        data = [{'Coluna': col} for col in object_columns]
        
        return html.Div(style={'display': 'flex', 'height': '100vh'}, children=[
            # Coluna esquerda para dados e matriz de dados ausentes
            html.Div(style={'flex': '1', 'padding': '20px', 'overflow': 'auto'}, children=[
                html.H1("Visualizador de Dados Multidimensionais"),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Arraste e solte ou ',
                        html.A('selecione um arquivo CSV')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    multiple=False
                ),
                html.Div(id='output-data-upload'),  # Tabela de dados
                html.H5("Matriz de Dados Ausentes:"),
                html.Img(id='missing-data-matrix', style={'marginTop': '20px'})
            ]),
            # Coluna direita com a tabela e botões
            html.Div(style={'flex': '1', 'padding': '20px', 'overflow': 'auto'}, children=[
                # Tabela para selecionar rótulo
                html.H2("Selecione uma Coluna de Rótulo:"),
                dash_table.DataTable(
                    id='label-column-table',
                    columns=[{'name': 'Coluna', 'id': 'Coluna'}],                   
                    data=data,
                    row_selectable='single',  # Permite seleção de uma linha
                    selected_rows=[],
                    style_table={'overflowX': 'auto'},
                    page_size=10,
                ),
                html.Button("Selecionar Rótulo", id='select-label-button', n_clicks=0),
                html.Div(id='selected-label-output'),  # Exibir rótulo selecionado
                
                # Tabela para novo DataFrame
                html.H2("Novo DataFrame:"),
                html.Div(id='new-dataframe-output'),  # Aqui você pode renderizar a nova tabela
                
                # Botão para redimensionar
                html.Button("Redimensionar", id='resize-button', n_clicks=0)
            ])
        ])

    def update_output(uploaded_file):
        if uploaded_file is not None:
            Dashboard.load_data(uploaded_file)  # Carrega o DataFrame
            return html.Div([
                html.H5("Dados Carregados:"),
                dash_table.DataTable(
                    data=Dashboard.dataframe.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in dashboard.dataframe.columns],
                    page_size=10,
                    style_table={'overflowX': 'auto'}
                )
            ])
        return html.Div("Carregue um arquivo CSV para visualizar os dados.")

    def setup_callbacks(self) -> None:

        @self.app.callback(
            [
                Output("output-data-upload", "children"),
                Output("missing-data-matrix", "src"),
            ],
            Input("upload-data", "contents"),
            State("upload-data", "filename"),
        )
        def update_output(
            contents: Optional[str], filename: Optional[str]
        ) -> Tuple[html.Div, Optional[str]]:
            if contents is not None:
                # Carregar o CSV para um DataFrame global
                self.dataframe = self.parse_contents(contents)

                # Mostrar os dados em uma tabela
                table: html.Div = html.Div(
                    [
                        html.H5(filename),
                        dash_table.DataTable(
                            data=self.dataframe.to_dict("records"),
                            columns=[
                                {"name": i, "id": i} for i in self.dataframe.columns
                            ],
                            page_size=10,
                            style_table={"overflowX": "auto"},
                        ),
                    ]
                )

                # Gerar a matriz de dados ausentes como imagem
                missing_data_img: str = generate_missing_data_matrix_from(
                    self.dataframe
                )

                return table, missing_data_img

            # Retornar conteúdo padrão se não houver arquivo carregado
            return html.Div(["Nenhum arquivo carregado."]), None

    @staticmethod
    def parse_contents(contents: str) -> pd.DataFrame:
        """Converte o conteúdo carregado em um DataFrame."""
        _: str
        content_string: str
        _, content_string = contents.split(",")
        
        decoded : bytes = base64.b64decode(content_string)
        dataframe: pd.DataFrame = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        return dataframe

    def run(self, debug: bool = True) -> None:        
        self.app.layout = self.layout()
        self.setup_callbacks()
        self.app.run_server(debug=debug)