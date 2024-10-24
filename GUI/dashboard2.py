import dash
from dash import dcc, html, Input, Output, State
import dash_table
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import missingno as msno
import io

app = dash.Dash(__name__)

# Variáveis globais para o DataFrame carregado
dataframe = pd.DataFrame()

# Layout do dashboard
app.layout = html.Div(
    style={
        "display": "grid",
        "gridTemplateColumns": "50% 50%",
        "gridTemplateRows": "50% 50%",
        "height": "100vh",
    },
    children=[
        # Canto superior esquerdo: Upload do arquivo
        html.Div(
            style={"padding": "20px"},
            children=[
                html.H2("Carregar DataFrame"),
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(
                        ["Arraste e solte ou ", html.A("selecione um arquivo CSV")]
                    ),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin": "10px",
                    },
                    multiple=False,
                ),
                html.Div(id="output-data-upload"),  # Tabela de dados
            ],
            className="top-left",
        ),
        # Canto inferior esquerdo: Matriz de dados ausentes
        html.Div(
            style={"padding": "20px"},
            children=[
                html.H2("Matriz de Dados Ausentes"),
                dcc.Graph(id="missing-data-matrix"),
            ],
            className="bottom-left",
        ),
        # Canto superior direito: Gráfico de coordenadas paralelas
        html.Div(
            style={"padding": "20px"},
            children=[
                html.H2("Gráfico de Coordenadas Paralelas"),
                dcc.Graph(id="parallel-coordinates"),
            ],
            className="top-right",
        ),
        # Canto inferior direito: Botões de filtragem
        html.Div(
            style={"padding": "20px"},
            children=[
                html.H2("Filtragem de Dados"),
                html.Button("Remover Dados Ausentes", id="remove-nan-button"),
                html.Button("Escolher Colunas", id="choose-columns-button"),
                html.Button("Escolher Rótulo", id="choose-label-button"),
                html.Button("Outro Filtro", id="other-filter-button"),
                # Janelas modais para cada filtro
                html.Div(
                    id="modal-popup",
                    children=[
                        html.Div(
                            style={
                                "position": "fixed",
                                "top": "50%",
                                "left": "50%",
                                "transform": "translate(-50%, -50%)",
                                "padding": "20px",
                                "backgroundColor": "white",
                                "border": "1px solid black",
                                "zIndex": "1000",
                            },
                            children=[
                                html.H2("Teste"),
                                html.Button("Cancelar", id="cancel-button"),
                                html.Button("Aplicar", id="apply-button"),
                            ],
                        )
                    ],
                    style={"display": "none"},
                ),
            ],
            className="bottom-right",
        ),
    ],
)


# Função para converter o conteúdo do upload para um DataFrame
def parse_contents(contents, filename):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    if "csv" in filename:
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    else:
        return None
    return df


# Callbacks para processar o carregamento do arquivo
@app.callback(
    [
        Output("output-data-upload", "children"),
        Output("missing-data-matrix", "figure"),
        Output("parallel-coordinates", "figure"),
    ],
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def update_output(contents, filename):
    global dataframe
    if contents is not None:
        dataframe = parse_contents(contents, filename)
        if dataframe is not None:
            # Matriz de dados ausentes usando Plotly
            msno_fig = msno.matrix(dataframe, figsize=(10, 6))
            msno_fig = ff.create_figure(msno_fig)
            # Gráfico de coordenadas paralelas
            fig_parallel = px.parallel_coordinates(dataframe)
            # Tabela dos dados carregados
            table = dash_table.DataTable(
                data=dataframe.to_dict("records"),
                columns=[{"name": i, "id": i} for i in dataframe.columns],
            )
            return table, msno_fig, fig_parallel
    return None, None, None


# Callback para exibir a modal
@app.callback(
    Output("modal-popup", "style"),
    [
        Input("remove-nan-button", "n_clicks"),
        Input("choose-columns-button", "n_clicks"),
        Input("choose-label-button", "n_clicks"),
        Input("other-filter-button", "n_clicks"),
    ],
)
def display_popup(n1, n2, n3, n4):
    if n1 or n2 or n3 or n4:
        return {"display": "block"}
    return {"display": "none"}


# Callback para esconder a modal
@app.callback(Output("modal-popup", "style"), Input("cancel-button", "n_clicks"))
def hide_modal(n_clicks):
    if n_clicks:
        return {"display": "none"}
    return dash.no_update


if __name__ == "__main__":
    app.run_server(debug=True)
