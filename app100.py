from dash import Dash, dcc, html, Input, Output, dash_table, State
import plotly.express as px
from downloading.downloader import get_playlist_order, download_spotify_playlist, gentable, get_filepath_speaks
import pandas as pd
import os
import pprint
import dash
from zipfile import ZipFile
from klub100 import stitch

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets = external_stylesheets)
df0 = pd.DataFrame()
df = pd.DataFrame(columns=["Songs","Downloaded","Delayed start","Duration", "Associated speak"])
table = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns],editable = True, id ="table" , row_selectable='multi',
        row_deletable=True,)

app.layout = html.Div([html.Div([
    dcc.Input(id='input-1-state', type='text', placeholder='Playlist URL',style = {"width" : "42%"}),
        html.Button(id='submit-button-state', n_clicks=0, children='Download')]),
    html.Div("Insert URL to download and toggle delayed start (in seconds)"), dcc.Upload(
        id='datatable-upload',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')," used in intermediate speaks (.zip)"
        ]),style={
            'width': '80%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed',
            'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
        },
    ),
    html.Table(dash_table.DataTable(id='datatable-upload-container'), style = {"width" : "85%", "margin" : "10px", "padding-right":"100px"} ),
    html.Button(id='submit-button-state2', n_clicks=0, children='Append speaks'),
    html.Div(id='output-state'),html.Hr(), html.Table(table,style = {"width" : "85%"} ),
    html.Hr(),
    html.Button(id='submit-button-state3', n_clicks=0, children='Generate klub100'),
    html.Table(dash_table.DataTable(id='check-data-table'), style = {"width" : "85%", "margin" : "10px", "padding-right":"100px"} ),
    html.Hr()])



def read_zipdir(filepath):
    with ZipFile(filepath, "r") as zip:
        list = zip.namelist()
        modlist = []
        for item in list:
            modlist.append(item)
        return modlist

def extract_speakzip(filepath):
    with ZipFile(filepath, "r") as zip:
        list = zip.namelist()
        modlist = []
        for item in list:
            read_normalize(os.path.join(os.get(cwd),"downloading",item))
        return modlist


@app.callback(Output("table","data"), Input("submit-button-state","n_clicks"),Input("submit-button-state2","n_clicks"),Input("submit-button-state3","n_clicks"),Input("input-1-state","value"), State('datatable-upload', 'filename'))
def press_download(btn1, btn2, btn3, value,filename):
    ctx = dash.callback_context

    if ctx.triggered[0]["prop_id"] == 'submit-button-state.n_clicks' and ctx.triggered[0]["value"] is not None:
        df, exportdir = gentable(value)
        return df.to_dict("records")
    if ctx.triggered[0]["prop_id"] == 'submit-button-state2.n_clicks' and ctx.triggered[0]["value"] is not None:
        df, exportdir = gentable(value)
        N = len(df["Associated speak"])
        insert = read_zipdir(get_filepath_speaks(filename))
        insert += [''] * (N - len(insert))
        df["Associated speak"] = insert
        return df.to_dict("records")
    if ctx.triggered[0]["prop_id"] == 'submit-button-state3.n_clicks' and ctx.triggered[0]["value"] is not None:
        df, exportdir = gentable(value)
        N = len(df["Associated speak"])
        insert = read_zipdir(get_filepath_speaks(filename))
        insert += [''] * (N - len(insert))
        df["Associated speak"] = insert
        stitch(df,exportdir,os.path.join(os.getcwd(),"downloading"))
        return df.to_dict("records")
        return

@app.callback(Output('datatable-upload-container', 'data'),
              Output('datatable-upload-container', 'columns'),
              Input('datatable-upload', 'contents'),
              State('datatable-upload', 'filename'))
def update_output(contents, filename):
    if contents is None:
        return [{}], []
    df0 = pd.DataFrame()
    print(filename)
    speaklist = read_zipdir(get_filepath_speaks(filename))
    df0["Contents"] = speaklist

    return df0.to_dict('records'), [{"name": i, "id": i} for i in df0.columns]


@app.callback(Output('check-data-table', 'data'),
              [Input('submit-button-state3', 'n_clicks'), State('table', 'data')])
def save_test_data(n, data):
    if n == 0:
        saved_test_data = None
    else:
        saved_test_data = data
        dfnew = pd.DataFrame.from_dict(data)
        print(dfnew)
    return saved_test_data

if __name__ == '__main__':
    app.run_server(host = "127.0.0.1", port = 5000,debug=True,dev_tools_hot_reload=False)
