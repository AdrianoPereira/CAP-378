from core.components import Div, Img, H6, P, Span, Br
from core.components import Graph, Link, Dropdown, RadioItems, DatePickerSingle
from datetime import datetime as dt
from core import constants as const
import pathlib
import os


def build_banner(app):
    return Div(
        id="banner",
        className="banner",
        children=[
            Img(src=app.get_asset_url("imgs/%s"%const.logo)),
            H6(const.header_title),

        ],
    )


def build_download_controls():
    return Div([
        Div(
            className="row",
            id="controls-dropdown",
            children=[
                Div(
                    id="dropdown-produtcs",
                    className="columns",
                    children=[
                        build_graph_title("Selcione um produto"),
                        Dropdown(
                            id='product',
                            options=[
                                {"label": prod, "value": prod}
                                for prod in const.products
                            ],
                            multi=False,
                            clearable=False,
                            value=const.products[4],
                        ),
                    ],
                ),
            ],
        )
    ])


def build_graph_title(title):
    return P(className="graph-title", children=title)


def build_menu():
    return Div(
        id='main-menu',
        children=[
            # Img(app.get_asset_url('icons/lightning.svg')),
            Link('GOES-16 ABI', href='/abi'),
            Link('GOES-16 GLM', href='/glm'),
            # Link('Aquisição de dados', href='/aquisition'),
        ],
    )


def build_footer():
    return Div(
        id='footer',
        children=[
            Span('© 2019 CAP-378 Tópicos em Observação da Terra.')
        ]
    )


def build_content():
    return Div([
        Div(
            id="message",
            className="row",
        ),
        Div(
            className="row",
            id="bottom-row",
            children=[
                Div(
                    id="lightning-container-2",
                    className="six columns",
                    children=[
                        # build_graph_title("Série temporal dos últimos 40 minutos"),
                        Graph(id="time-serie"),
                    ],
                ),
                Div(
                    id="lightning-container-1",
                    className="six columns",
                    children=[
                        # build_graph_title("Série temporal dos últimos 40 minutos"),
                        Graph(id="lightning-by-km"),
                    ],
                )
            ],
        ),
        # Div(
        #     className="row",
        #     children=[
        #         Div(
        #             id="lightning-container-1",
        #             className="five columns",
        #             children=[
        #                 # build_graph_title("Série temporal dos últimos 40 minutos"),
        #                 Graph(id="lightning-by-km"),
        #             ],
        #         )
        #     ],
        # ),
        Div(
            className="row",
            id="bottom-row",
            children=[
                Div(
                    id="lightning-container-3",
                    className="four columns",
                    children=[
                        # build_graph_title("Densidade de descargas elétricas nos úlltimos 30 minutos"),
                        Graph(id="histogram"),
                    ],
                ),
                Div(
                    id="lightning-container-4",
                    className="eight columns",
                    children=[
                        # build_graph_title("Densidade de descargas elétricas nos úlltimos 30 minutos"),
                        Graph(id="abi1"),
                    ],
                ),
                # Div(
                #     id="lightning-container-5",
                #     className="four columns",
                #     children=[
                #         # build_graph_title("Densidade de descargas elétricas nos úlltimos 30 minutos"),
                #         Graph(id="abi2"),
                #     ],
                # ),
            ],
        ),
    ])


def build_header(app):
    return Div([
        Div(
            id="top-row",
            children=[
                Div(
                    className="row",
                    id="top-row-header",
                    children=[
                        Div(
                            id="header-container",
                            children=[
                                build_banner(app),
                                P(
                                    id="instructions",
                                    children=const.header_description,
                                ),
                                Span("Destaque um estado", className='title-custom'),
                                Dropdown(
                                    id="state-select",
                                    options=[
                                        {"label": state['name'], "value": state['id']}
                                        for state in const.states
                                    ],
                                    multi=False,
                                    clearable=False,
                                    value=const.states[25]['id'],
                                ),
                                Br(),
                                Div(id='predict'),
                                Div(
                                    id="lightning-container-1",
                                    className="twelve columns",
                                    children=[
                                        # build_graph_title("Total de raios"),
                                        Graph(id="lightnings"),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
                Div(
                    className="row",
                    id="top-row-graphs",
                    children=[
                        Div(
                            id="well-map-container",
                            children=[
                                build_graph_title("Visualização (GLM)"),
                                Span('Estilo do mapa', style=dict(color='#FFFFFF')),
                                RadioItems(
                                    id="mapbox-view-selector",
                                    options=[
                                        {"label": "dark", "value": "dark"},
                                        {"label": "outdoors", "value": "outdoors"},
                                        {"label": "basic", "value": "basic"},
                                        {"label": "satellite", "value": "satellite"},
                                        {
                                            "label": "satellite-street",
                                            "value": "mapbox://styles/mapbox/satellite-streets-v9",
                                        },
                                    ],
                                    value="dark",
                                ),
                                Graph(
                                    id="states-mapview",
                                    figure={
                                        "layout": {
                                            "paper_bgcolor": "#192444",
                                            "plot_bgcolor": "#192444",
                                        }
                                    },
                                    # style=dict(height='98%'),
                                    config={"scrollZoom": True, "displayModeBar": True},
                                ),
                                Br(),
                                Div(
                                    className="",
                                    id="bottom-row",
                                    children=[
                                        # build_graph_title("Maior incidência de raios nos últimos minutos"),
                                        Graph(id="lightning-by-state"),
                                    ],
                                )
                            ],
                        ),
                    ],
                ),
            ],
        )
    ])