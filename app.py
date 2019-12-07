from core import numpy as np
from core import Wrapper
from core.components import Dropdown, Graph, RadioItems, Location, Link
from core.components import Div, H6, Img, P, Span, Hr, DataTable, A
from core import go
from core import Input, Output, State
from core import constants as const
from core.components import build_banner, build_graph_title
from core.pages import build_glm_page, build_abi_page, build_download_page
import subprocess as sp
import pathlib
from core import os
import pandas as pd
import geopandas as gpd
from datetime import datetime as dt


# configure server
app = Wrapper(__name__, meta_tags=const.meta_tags)
app.config["suppress_callback_exceptions"] = True
app.title = const.title
server = app.server

# credentials
mapbox_access_token = const.credentials['mapbox']

app.layout = Div([
    Location(id='url', refresh=False),
    Div(id='page-content')
])
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/abi':
        return build_abi_page()
    elif pathname == '/aquisition':
        return build_download_page()
    else:
        return build_glm_page(app)


@app.callback(
    [Output("states-mapview", "figure"), Output("histogram", "figure"),
    Output("lightnings", "figure"), Output("lightning-by-state", "figure"),
    Output("time-serie", "figure"), Output("predict", "children"), Output("lightning-by-km", "figure"),
     Output("abi1", "figure")],
     # Output("abi2", "figure")],
    [Input("state-select", "value"), Input("mapbox-view-selector", "value")]
)
def update_mapview_states(state, style):
    FILE_PATH = str(pathlib.Path(__file__).parent.resolve())
    path = '.data/csv/glm' #path of files GLM
    path = os.path.join(FILE_PATH, path)
    files = sorted(os.listdir(path))
    files = list(filter(lambda x: x.endswith('.csv'), files))[-3:]
    files = [os.path.join(path, file) for file in files]

    state = const.states[state]
    data = list()

    total_l, lons, lats = [], [], []
    time = 30
    total = list()
    dfs = []
    colors = ['red', 'green', 'blue'][::-1]
    now = dt.utcnow()
    km_area = []
    print('files--->>', len(files))
    for color, file in enumerate(files):
        print('GLM file: ', file)
        df = pd.read_csv(file)
        dfs.append(df)
        print(df.head())
        x = df['flash_lon'].values
        y = df['flash_lat'].values

        group = df.query('state != "OUTSIDE"').groupby(['state']).count()
        group = group.sort_values('flash_lat', ascending=False)
        states = group.index
        s_lightnings = group['geometry'].values
        temp = int()
        try:
            temp = group.loc[state['name']].values[0]
        except KeyError:
            temp = 0
        total.append(temp)
        print(group)
        lightning_by_km = {}
        for index, row in zip(states, s_lightnings):
            area = list(filter(lambda x: x['name'] == index, const.states ))[0]['area']
            # lightning_by_km['%s (%.2fkm²)'%(index, area)] = row/area
            lightning_by_km[index] = row / area

        print('color---->>> ', )
        km_area.append(
            go.Bar(y=list(lightning_by_km.values()), x=list(lightning_by_km.keys()),
                   name='%s-%s minutos atrás'%(time-10, time),  marker=dict(color=colors[color]))
        )

        total_l.append(
            go.Bar(y=states[:5], x=s_lightnings[:5], opacity=(.33*(color+1.0))/1,
                   marker=dict(color='rgb(255, 255, 255)'),
                   name='%s-%s minutos atrás'%(time-10, time), orientation='h')
        )

        print((time-10, time))
        data.append(
            go.Scattermapbox(
                lat=y,
                lon=x,
                mode="markers",
                name='GLM Flashs (%s-%s minutos atrás)'%(time-10, time),
                marker=dict(color=colors[color])
            )
        )
        time -= 10

        for lon, lat in zip(x, y):
            lons.append(lon)
            lats.append(lat)
    g_km_by_area = go.Figure(data=km_area)
    g_km_by_area.update_layout(
        template='plotly_white',
        title=dict(text="Média de raios por km² nos últimos 30 minutos<br>%s-%s-%s %s:%s UTC"% (str(now.day).zfill(2),
            str(now.month).zfill(2), str(now.year).zfill(2), str(now.hour).zfill(2), str(now.minute).zfill(2)),
                   xanchor="center", y=0.9, x=0.5, yanchor="top"),
        font=dict(color="rgb(25, 36, 68)"),
    )


    dfs = pd.concat(dfs)
    times = sorted(np.unique(dfs['timestamp']))
    ts_size = len(times)
    time_serie = {}
    for _, row in const.shp_brazil.iterrows():
        time_serie[row['NOMEUF2']] = np.zeros(ts_size)

    group = dfs.groupby(['timestamp', 'state']).agg({'state': 'count'})
    group.head()
    idx = 0
    old_index = group.index.get_level_values(0)[0]
    for index, value in group.iterrows():
        if index[1] == 'OUTSIDE':
            continue
        if index[0] != old_index:
            old_index = index[0]
            idx += 1
        time_serie[index[1]][idx] = value[0]

    g_time_serie = []
    for key in time_serie.keys():
        g_time_serie.append(go.Scatter(y=time_serie[key], name=key))
    g_time_serie = go.Figure(
        data=g_time_serie,
    )
    g_time_serie.update_layout(
        template='plotly_white',
        title=dict(text="Total de raios computados nos últimos 30 minutos nos estados brasileiros<br>%s-%s-%s %s:%s UTC"% (str(now.day).zfill(2),
            str(now.month).zfill(2), str(now.year).zfill(2), str(now.hour).zfill(2), str(now.minute).zfill(2)),
                   xanchor="center", y=0.9, x=0.5, yanchor="top"),
        font=dict(color="rgb(25, 36, 68)"),
    )

    predict = H6(children='Total de raios')

    s_total = sum(total)
    pie = go.Figure(
        go.Pie(labels=['Total raios no estado (%s)'%s_total,
                       'Total raios fora do estado (%s)'%(len(lons)-s_total)],
               values=[s_total, len(lons)-s_total], hole=.6, marker_colors=('#8f8f8f', '#dcdcdc'))
    )

    pie.update_layout(
        paper_bgcolor='rgb(31, 44, 86)',
        plot_bgcolor='rgb(31, 44, 86)',
        legend_orientation="h",
        width=400,
        legend={
            "font": {
                "color": "#FFFFFF",
            }
        },
        annotations=[
            go.layout.Annotation(text='%.1f raios/km²'%(s_total/state['area']),showarrow=False),
        ],
        title=dict(
            text='%s nos últimos 30 minutos<br>%s-%s-%s %s:%s UTC' % (state['name'],
                str(now.day).zfill(2), str(now.month).zfill(2), str(now.year).zfill(2), str(now.hour).zfill(2),
                str(now.minute).zfill(2)),
            xanchor="center",
            y=0.9, x=0.5, yanchor="top"
        ),
        font=dict(color="#FFFFFF"),
        # legend_orientation="h",
        xaxis_title='Total de raios'
    )

    mapview = go.Figure(data=data)
    mapview.update_layout(
        title='ok',
        clickmode="event+select",
        showlegend=True,
        autosize=True,
        hovermode="closest",
        margin=dict(l=0, r=0, t=0, b=0),
        # height=500,
        # width=1220,
        annotations=[
            go.layout.Annotation(text='GOES-16: Produto Flash do GLM. %s-%s-%s %s:%s UTC'%(str(now.day).zfill(2),
                                 str(now.month).zfill(2), str(now.year).zfill(2), str(now.hour).zfill(2),
                                 str(now.minute).zfill(2)), showarrow=False, y=0.05, x=.990, borderpad=10,
                                 font=dict(color='#FFFFFF'),  bgcolor="rgba(31, 44, 86, .2)"),
        ],
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(lat=state['center'][1], lon=state['center'][0]),
            pitch=0,
            zoom=4.8,
            style=style,
        ),
        legend=dict(
            bgcolor="#1f2c56",
            orientation="h",
            font=dict(color="white"),
            x=0,
            y=0,
            yanchor="bottom",
        ),
    )
    g_lightning_by_state = go.Figure(data=total_l)
    g_lightning_by_state.update_layout(
        title=dict(
            text='Total de raios nos estados com maior incidência nos últimos 30 minutos<br>%s-%s-%s %s:%s UTC' % (
                str(now.day).zfill(2), str(now.month).zfill(2), str(now.year).zfill(2), str(now.hour).zfill(2),
                str(now.minute).zfill(2)),
            xanchor="center",
            y=0.9, x=0.5, yanchor="top"
        ),
        paper_bgcolor='rgb(25, 36, 68)',
        plot_bgcolor='rgb(25, 36, 68)',
        font=dict(color="#FFFFFF"),
        legend_orientation="h",
        # xaxis_title='Total de raios'
    )

    data_hist = list()
    data_hist.append(
        go.Scatter(
            x=lons, y=lats, mode='markers', name='points',
            marker=dict(color='rgba(0,0,0,0.2)', size=1, opacity=0.3)
        )
    )

    data_hist.append(
        go.Histogram2dcontour(
            x=lons, y=lats, name='density', ncontours=15,
            colorscale='Hot', reversescale=True, showscale=True
        )
    )

    data_hist.append(
        go.Histogram(
            x=lons, name='Densidade na longitude',
            marker=dict(color='#000000'),
            yaxis='y2'
        )
    )

    data_hist.append(
        go.Histogram(
            y=lats, name='Densidade na latitude', marker=dict(color='#000000'),
            xaxis='x2'
        )
    )

    layout_hist = go.Layout(
        title=dict(text="Densidade de descargas elétricas nos úlltimos 30 minutos<br>%s-%s-%s %s:%s UTC"% (str(now.day).zfill(2),
            str(now.month).zfill(2), str(now.year).zfill(2), str(now.hour).zfill(2), str(now.minute).zfill(2)),
                   xanchor="center", y=0.9, x=0.5, yanchor="top"),
        font=dict(color="rgb(25, 36, 68)"),
        plot_bgcolor='rgb(255, 255, 255)',
        showlegend=False,
        autosize=False,
        yaxis_title="Latitude",
        xaxis_title="Longitude",
        xaxis=dict(
            domain=[0, 0.84],
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            domain=[0, 0.83],
            showgrid=False,
            zeroline=False
        ),
        margin=dict(
            # t=50
        ),
        hovermode='closest',
        bargap=0,
        xaxis2=dict(
            domain=[0.85, 1],
            showgrid=False,
            zeroline=False
        ),
        yaxis2=dict(
            domain=[0.85, 1],
            showgrid=False,
            zeroline=False
        ),
    )

    hist2d = go.Figure(data=data_hist, layout=layout_hist)

    path = path.replace('glm', 'abi')
    files = sorted(os.listdir(path))
    files = list(filter(lambda x: x.endswith('.csv'), files))[-3:]
    files = [os.path.join(path, file) for file in files]
    abi1 = []
    time = 30
    for i, file in enumerate(files):
        print('ABI file: ', file)
        df = pd.read_csv(file)
        temp = {}
        for _, row in df.iterrows():
            temp[row['state']] = {
                'min': row['min'], 'mean': row['mean'], 'max': row['max'], 'std': row['std']
            }
        labels = list(temp.keys())
        values = [temp[x]['mean'] for x in temp.keys()]
        errors = [temp[x]['std'] for x in temp.keys()]
        abi1.append(
            go.Bar(x=labels, y=values, error_y=dict(type='data', array=errors),
                   name='%s-%s minutos atrás'%(time-10, time), marker=dict(color=colors[i])),
                   # marker=dict(color=values, showscale=False, colorscale='Jet'))
        )
        time -= 10

    abi1 = go.Figure(
        data=abi1
    )
    abi1.update_layout(
        title=dict(
            text='Temperatura [K] do topo das nuvens nos últimos minutos<br> ABI CH13 %s-%s-%s %s:%s UTC' % (
                str(now.day).zfill(2), str(now.month).zfill(2), str(now.year).zfill(2), str(now.hour).zfill(2),
                str(now.minute).zfill(2)),
            xanchor="center",
            y=0.9, x=0.5, yanchor="top"
        ),
        # xaxis=dict(categoryorder='array', categoryarray=[x for _, x in sorted(zip(values, labels))]),
    )

    print(len(files), '<<---fies len')
    return mapview, hist2d, pie, g_lightning_by_state, g_time_serie, predict, g_km_by_area, abi1


if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')
    # app.run_server(debug=True)
