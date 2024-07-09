from pathlib import Path

import base64
import datetime
import io
import os 

import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
from dash import dash_table
import plotly.express as px
import numpy as np
import pandas as pd
import csv

app = dash.Dash(__name__, suppress_callback_exceptions=True)

#add server
server = app.server

app.layout = html.Div([
    html.H1(
        "Two Pyrometer Parser",
        style = {
        'text-align':'left',
        'color':'#6A5ACD',
        'text-indent': '2%'
        }
        ),

    #Input 1 - one pyrometer
    html.P("One Pyro Path: ",
        style = {
        'text-align':'left',
        'color':'#6A5ACD',
        }),
    dcc.Input(id='OnePfilepath', value='', type='text',style={'width': '25%'}),

    html.Br(),

    html.P("One Pyro Shift Left: ",
        style = {
        'text-align':'left',
        'color':'#6A5ACD',
        }),
    dcc.Input(id='Oneshift', value='', type='text',style={'width': '12.5%'}),

    html.Br(),
    html.P("One Pyro Range: ",
        style = {
        'text-align':'left',
        'color':'#6A5ACD',
        }),
    dcc.Input(id='Onebeg', value='', type='text',style={'width': '12.5%'}),
    dcc.Input(id='Oneend', value='', type='text',style={'width': '12.5%'}),

    html.Br(),
    html.Br(),
    html.Br(),

    #Input 2 - Two Pyrometer
    html.P("Two Pyro Path: ",
        style = {
        'text-align':'left',
        'color':'#6A5ACD',
        }),
    dcc.Input(id='TwoPfilepath', value='', type='text',style={'width': '25%'}),
    html.Br(),

    html.P("Two Pyro Shift Left: ",
        style = {
        'text-align':'left',
        'color':'#6A5ACD',
        }),
    dcc.Input(id='Twoshift', value='', type='text',style={'width': '12.5%'}),

    html.Br(),
    html.P("Two Pyro Range: ",
        style = {
        'text-align':'left',
        'color':'#6A5ACD',
        }),
    dcc.Input(id='Twobeg', value='', type='text',style={'width': '12.5%'}),
    dcc.Input(id='Twoend', value='', type='text',style={'width': '12.5%'}),

    html.Br(),
    html.Br(),
    html.Br(),


    #Submit Button
    html.P("Enter Download Location: ",
        style = {
        'text-align':'left',
        'color':'#6A5ACD',
        }),
    dcc.Input(id='downloadloc', value='', type='text',style={'width': '25%'}),
    html.Br(),
    html.Br(),
    html.Button(id='submit-button', type='submit',children='Download File Data'),
    html.Br(),
    html.Br(),
    
    html.Div(id='output_div'),

    html.Br(),
    html.Div(id='output-datatable'),

])


#Button 1
@app.callback(Output('output_div', 'children'), 
            [Input('submit-button', 'n_clicks')], 
            [State('OnePfilepath', 'value')],
            [State('Oneshift', 'value')],
            [State('Onebeg', 'value')],
            [State('Oneend', 'value')],
            [State('TwoPfilepath', 'value')],
            [State('Twoshift', 'value')],
            [State('Twobeg', 'value')],
            [State('Twoend', 'value')],
            [State('downloadloc', 'value')],
            )
def update_output(clicks, onepyropath, oneshift, onebeg, oneend, twopyropath, twoshift, twobeg, twoend,downloadloc):
    if clicks is not None:
        try:
            #Parsing one Pyro Data

            if onepyropath != '' and downloadloc !='':
                onepyropath = onepyropath.replace('"', '')
                onedf = pd.read_table(onepyropath, encoding="ISO-8859-1",low_memory=False)
                headers = onedf.loc[ 18 , : ].tolist()#list of headers to be selected
                onedf=onedf.drop(range(0,19)) #drops first few rows (removes non-data)
                onedf = onedf.set_axis(list(headers), axis=1)   
                col = [0,44] #Select the columns of focus, 0, 44 is temp
                onedf = onedf.iloc[:,col]
                onedf = onedf.apply(pd.to_numeric)
                if onebeg != '':
                    onedf = onedf.drop(onedf[onedf.i.astype(int) <= int(onebeg)].index)
                if oneend != '':
                    onedf = onedf.drop(onedf[onedf.i.astype(int) >= int(oneend)].index)
                if oneshift != '':
                    onedf['temp'] = onedf.temp.shift(-int(oneshift))
                onedf['index'] = onedf['i']
                onedf = onedf.set_index('index')
                if twopyropath == '':
                    onedf.to_csv(os.path.join(downloadloc,r'onepyrodata.csv'),index = False)

                


            #Parsing two Pyro Data
            if twopyropath != ''and downloadloc !='':
                twopyropath = twopyropath.replace('"', '')
                twodf = pd.read_table(twopyropath,sep =',',skipinitialspace=True, encoding="ISO-8859-1",header = 20,on_bad_lines = 'warn',engine='python')
                #twodf.to_csv(str("wadadwdwadwdadwad")+".csv", index=False)
                col = [0,4] #Select the columns of focus, 0, 4 is temp
                twodf = twodf.iloc[:,col]
                twodf.columns = ["time","temp2"]
                twodf.drop(twodf.tail(1).index,inplace=True) #drop the last (1) row ---None
                twodf['temp2'] = twodf['temp2'].str.split('\t').str[1] #Removes unnnessisary stuff from temp coloumn
                twodf = twodf.drop_duplicates(subset=['time']) # Deletes two pyrometer double count
                twodf['i2'] = list(range(1, len(twodf) + 1)) #Adds index column
                del twodf['time'] # deletes unneeded Time column
                twodf = twodf[['i2', 'temp2']] # Swaps the columns i and temp
                twodf = twodf.apply(pd.to_numeric)
                if twobeg != '':
                    twodf = twodf.drop(twodf[twodf.i2.astype(int) <= int(twobeg)].index)
                if twoend != '':
                    twodf = twodf.drop(twodf[twodf.i2.astype(int) >= int(twoend)].index)
                if twoshift != '':
                    twodf['temp2'] = twodf.temp2.shift(-int(twoshift))
                twodf['index'] = twodf['i2']
                twodf = twodf.set_index('index')
                if onepyropath == '':
                    twodf.to_csv(os.path.join(downloadloc,r'twopyrodata.csv'),index = False)
                
            if onepyropath !='' and twopyropath != ''and downloadloc !='':
                #"C:\Users\KenCL\Documents\Dashboard\240703-164505 - Growth-Etch - GLCT_0491 - GE_AB1_049 - .dat"
                merged = pd.concat([onedf, twodf], axis=1, join="inner")
                merged['t diff'] = merged['temp'] - merged['temp2']
                merged.to_csv(os.path.join(downloadloc,r'mergedpyrodata.csv'),index = False)
                
            
                

            #if onedf not empty and twodf not empty:
            
            
        except Exception as e:
            print(e)
    
    return None






#Call in  onepyrometer data
# call in two pyrometer data
#extract col index values for one pyrmeter and two pyrometer
#create two list lis values for each pyrometer containing the index valye and th etmperature value
# Calulate overlap betwee the list
#overlap contains sharing time index between the two index lists (create shared i index assinged to both)
#recipriocol valye is indexed list 

if __name__ == '__main__':
    app.run_server(debug=True)
