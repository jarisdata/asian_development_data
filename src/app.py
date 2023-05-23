# data wrangling
import pandas as pd
import numpy as np

import pandas.plotting as pdplot
import plotly.express as px
from plotly.subplots import make_subplots
import chart_studio.plotly as py
import plotly.graph_objects as go

# Dash
import dash
#from jupyter_dash import JupyterDash
from dash import Dash, dcc, Output, Input, State  # pip install dash
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
from dash import html



# 1. Loading the data
main_data = pd.read_csv('https://raw.githubusercontent.com/jarisdata/asian_development_data/main/main_data_export_cor.csv')


# Doorstep conditions
dcp1_cols = ['dcp1_ref_clean_admin','dcp1_ref_clean_courts',
            'dcp1_pow_veto_players','dcp1_pow_legit']
            
dcp2_cols = ['dcp2_ref_statecapacity','dcp2_ref_partyinstitut_own', 
            'dcp2_pow_csoparticipation','dcp2_pow_socialfoundationsize']
            

dcp3_cols = ['dcp3_ref_militarymerit','dcp3_ref_militaryinfluence',    
     'dcp3_pow_violrepress_ammin','dcp3_pow_nonviolrepress_ammin']            
     

dce1_cols = ['dce1_ref_domfin','dce1_ref_extfin',
            'dce1_pow_govrev','dce1_pow_findev']

dce2_cols = ['dce2_ref_industrialpolicyindex','dce2_ref_tradeimf',
            'dce2_pow_manufacturing_gm','dce2_pow_sitceti']
            
dce3_cols = ['dce3_ref_accesstopublicservices','dce3_ref_totsocialexpenditure',
            'dce3_pow_union','dce3_pow_humancapital_efa'] 

# All individual features
dc_all_cols = dcp1_cols + dcp2_cols + dcp3_cols + dce1_cols + dce2_cols + dce3_cols

# All political features
dcp_cols = dcp1_cols + dcp2_cols + dcp3_cols

# All economic features
dce_cols = dce1_cols + dce2_cols + dce3_cols


# Medium level of aggreation:
dce_pca_cols = ['dce1_pca','dce2_gm','dce3_pca']
dcp_pca_cols = ['dcp1_pca','dcp2_pca','dcp3_pca']
dcpe_pca_cols = dce_pca_cols + dcp_pca_cols

# Medium level of aggreation:
dce_cols = ['dce1','dce2','dce3']
dcp_cols = ['dcp1','dcp2','dcp3']
dcpe_cols = dce_cols + dcp_cols

# Highest level of aggregation:
dc_cols = ['dcp','dce']
dc_pca_cols = ['dcp_pca','dce_pca']



# wide version
dash_data = main_data[['iso','country','year','rgdpc_pwt','income_justice','income_class', 'io','ioe','iop','dc','dce','dcp','dcp1','dcp2','dcp3','dce1','dce2','dce3']]
#dash_data['year'] = dash_data.year.astype('Int64')
dash_data = dash_data.rename({
        'rgdpc_pwt':'Income per capita', 'income_justice':'Income justice', 'income_class' : 'Income class', 
     'io':'Institutions','ioe':'Economic institutions','iop':'Political institutions',
     'dc':'Doorstep conditions', 'dce':'Economic doorstep conditions', 'dcp':'Political doorstep conditions',
     'dcp1': 'Legitimacy','dcp2':'Co-optation','dcp3':'Repression',
     'dce1':'Financial Development','dce2':'Industrialization','dce3':'Human Development'
     }, axis=1)

# long version
#melted_data = main_data.melt(id_vars=['iso','country','year'])

# For bar chart
dc_plot = pd.merge(main_data[['iso','year']], main_data[dc_all_cols], how='inner',left_index=True, right_index=True)


# 2. Plots

# Choropleth map

def choropleth_plot_func(selected_year):
    fig = px.choropleth(data_frame=dash_data.loc[dash_data['year'] == selected_year],
                        locations='iso',
                        locationmode="ISO-3",
                        height=600,
                        color='Doorstep conditions',
                        #animation_frame='year',
                        #category_orders={'year': list(range(1975, 2014))},
                        color_continuous_scale='RdYlGn',
                        range_color=[0, 1],
                        custom_data=['year', 'country'],
                        scope='asia',
                        )

    # Set the map projection and range
    fig.update_geos(
                lonaxis_range=[52, 143],
                lataxis_range=[-10, 45],
    )

    fig.update_layout(
                        width=800, 
                        height=500,
                geo=dict(bgcolor='white'),
                #coloraxis_colorbar_x=-0.15
                coloraxis_colorbar=dict(
                    title = None,
                    x=-0.020,
                    y=0.4,
                    #ticklabelposition='inside left',
                    ticks='inside',
                        ticklabelposition = 'inside', ticksuffix = '                  ', ticklabeloverflow='allow', tickfont_color='darkslategrey',
                        tickvals=[0.25, 0.5, 0.75], ticktext=["0.25: Fragile", "0.5: Basic", "0.75: Mature"],
                    ticklen=10,
                    tickcolor='black',
                    thickness=20,
                    len=1.1,
                    bgcolor='white',
                    title_font=dict(size=12)
                        )
                    )
    fig.add_scattergeo(locations=dash_data['iso'], text=dash_data['country'], mode='text')
    
    return(fig)

# 2.2 Polar Chart

def radar_plot_func(extract_iso, extract_year, dash_data=dash_data):

    #fig = None

    if not dash_data.loc[(dash_data.iso == extract_iso) & (dash_data.year == extract_year)].empty:            
            
        df_bar = dash_data.loc[(dash_data.iso == extract_iso
                                ) & (dash_data.year == extract_year)]
        df_radar = df_bar.T[12:].reset_index()
        if df_radar.shape[1] == 2:
            df_radar.columns = ['variable','values']

            temp_row = df_radar.iloc[3].copy()
            df_radar.iloc[3] = df_radar.iloc[5]
            df_radar.iloc[5] = temp_row
            df_polar = df_radar.copy()

            fig = (go.Figure(data=go.Barpolar(
                                        r=df_polar['values'], 
                                        theta=df_polar['variable'],
                                        marker_color=['#e9d561','#9ed56b','#e3807d','#e096e9','#7aa3e5','#efa670'],
                                        marker_line_color="black",
                                        marker_line_width=1,
                                        opacity=0.8,
                                        hovertemplate='Variable: %{theta}<br>Value: %{r}<br>Year: %{text}',
                                        text=df_bar['year'],
                                          
                                        )))

            fig.update_layout(
                #title = f'{extract_country} in {extract_year}',
                width = 650,
                height = 530,
                showlegend = False,
                template=None,
                polar = dict(
                    radialaxis = dict(range=[0, 1], showticklabels=True, ticks=''),
                    angularaxis = dict(showticklabels=True, ticks='')
                            ))

            fig.update_polars(angularaxis_rotation=120)
   
    else:
        df_empty = pd.DataFrame({})
        fig = (go.Figure(data=go.Barpolar(
                                r=df_empty, 
                                theta=df_empty,
                                #marker_color=['#e9d561','#9ed56b','#e3807d','#e096e9','#7aa3e5','#efa670'],
                                #marker_line_color="black",
                                #marker_line_width=1,
                                opacity=0.8,
                                )))

        fig.update_layout(
            width = 650,
            height = 550,
            showlegend = False,
            template=None,
            polar = dict(
                radialaxis = dict(range=[0,1], showticklabels=True, ticks=''),
                angularaxis = dict(showticklabels=False, ticks='')
                        ))

        fig.update_polars(angularaxis_rotation=120)

    return(fig)


# 2.3 Bar chart

# Bar chart

def plot_dc_bar(extract_dc, extract_iso, extract_year, dc_plot=dc_plot):
    
    col_names = {'dcp1_ref_clean_admin':'Bureaucracy','dcp1_ref_clean_courts':'Courts','dcp1_pow_veto_players':'Veto<br>Players','dcp1_pow_legit':'Legitimacy',
        'dcp1_ref_impartialpubadmin': 'Public<br>Administration','dcp1_ref_appointmentcriteria':'Meritocratic<br>Hiring', 'dc1p_clean_admin':'Clean<br>Bureaucracy', 'dcp1_clean_courts':'Clean Courts','dcp1_ref_impartialcourts':'Impartial Courts',
                            'dcp1_ref_integritylegsys':'Legal<br>System','dcp1_ref_polcorruption':'Corruption', 'dcp1_pow_policydecision50':'Veto<br>Players',
                            'dcp1_pow_legitlb':'Acceptance from followers','dcp1_pow_legitclb':'Acceptance from cotingent bloc','dcp1_pow_legitob':'Acceptance from opposition', 'dcp1_legit':'Legitimacy',
                            'dcp2_ref_statecapacity':'State<br>Capacity','dcp2_pow_csoparticipation':'Civil<br>Society', 'dcp2_ref_partyinstitut_own':'Party<br>Institutionalization','dcp2_ref_indpolorgengage':'Independent<br>Political<br>Organizations', 'dcp2_ref_csoparticipation':'Civil<br>Society<br>Organizations',
                            'dcp2_pow_socialfoundationsize':'Social<br>Foundation', 'dcp2_ref_polorg':'Political<br>Organizations',
                            'dcp3_ref_militarymerit':'Professional<br>Military','dcp3_ref_militaryinfluence':'Political<br>Intervention<br>of Military','dcp3_pow_violrepress_ammin':'Violent<br>Repression','dcp3_pow_nonviolrepress_ammin':'Non-violent<br>Repression',
                            'dce1_ref_supervision':'Financial<br>Supervision','dce1_ref_domfin':'Domestic<br>Regulations','dce1_ref_extfin':'Capital<br>Account<br>Regulation','dce1_pow_govrev':'Government<br>Revenue','dce1_pow_findev':'Financial<br>Depth',
                            'dce2_ref_industrialpolicyscore':'Industrial<br>Policy','dce2_ref_industrialpolicyindex':'Industrial<br>Policy','dce2_ref_tradeimf':'Trade<br>Openness','dce2_ref_accestostatebusi':'Access to<br>State<br>Business', 
                            'dce2_pow_manufacturing_gm':'Manufacturing<br>Companies','dce2_pow_sitceti':'Economic<br>Complexity',
                            'dce3_ref_manufacemp':'Manufacturing<br>Employment','dce3_ref_accesstopublicservices':'Public<br>Services','dce3_ref_totsocialexpenditure':'Social<br>Expenditure',
                            'dce3_pow_union':'Trade<br>Unions','dce3_pow_humancapital_efa':'Human<br>Capital'                            
                }   
    
    dc_names = {'dcp1': 'Legitimacy','dcp2':'Co-optation','dcp3':'Repression',
    'dce1':'Financial Development','dce2':'Industrialization','dce3':'Human Development'}
    
    color_map = {
        'dce1': '#efa670',
        'dce2': '#7aa3e5',
        'dce3': '#e096e9',
        'dcp1': '#e9d561',
        'dcp2': '#9ed56b',
        'dcp3': '#e3807d'
        }
    
    fig_dc_bar = None
    

    
    for key, value in dc_names.items():
        if value == extract_dc:
            extract_dc_key = key
        

            condition = (dc_plot.iso == extract_iso) & (dc_plot.year == extract_year)
            dc_plot_select = dc_plot.loc[condition, dc_plot.columns.str.contains(extract_dc_key)]
            
            color_map = {
            'dce1': '#efa670',
            'dce2': '#7aa3e5',
            'dce3': '#e096e9',
            'dcp1': '#e9d561',
            'dcp2': '#9ed56b',
            'dcp3': '#e3807d'
            }
    
    
    if not dc_plot_select.empty:            
                    
        fig_dc_bar = px.bar(data_frame=dc_plot_select.T)
        fig_dc_bar.update_traces(marker_color=color_map[extract_dc_key[:4]],
                                width=0.8,
                                text=dc_plot_select.T.values.flatten(),  # Set the text values to be displayed on the bars
                                textposition='inside',  # Position the text in the middle of the bars
                                textfont=dict(
                                            size=14,  # Set the font size
                                            #color='black',  # Set the font color
                                            family='Arial'  # Set the font family
                                            )
                                )
        fig_dc_bar.update_layout(
                title = {'text': f'{extract_dc}',
                        'y': 0.9,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font': {'size': 15}    
                        },
                showlegend=False, 
                autosize=False,
                width=600, 
                height=300, 
                bargap=0.05,
                xaxis=dict(
                    ticktext=[col_names.get(col, col) for col in dc_plot_select.columns],
                    tickvals=list(range(len(dc_plot_select.columns))),
                    #tickmode='array',
                    tickangle=0,
                    title='',
                    #automargin=True
                    ),
                yaxis=dict(
                    title='',
                    showticklabels=False,
                    range=[0,1]
                    )
                )
        fig_dc_bar.update_yaxes(automargin=True)
                
    else:
        df_empty = pd.DataFrame({})
        fig_dc_bar = px.bar(data_frame=df_empty.T,
                            range_y=[0,1])
        fig_dc_bar.update_layout(
        title = {'text': 'No data',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'    
        },            
        showlegend=False, 
        width=650, 
        height=350, 
        bargap=0.05,
        xaxis=dict(
        showticklabels=False,
        title=''),
        yaxis=dict(
        title='',
        showticklabels=False))
        
    return(fig_dc_bar)




# 2.4 Line chart: Doorstep Conditions

def dc_line_plot_func(extract_iso,selected_year):

    fig = None
    
    df=dash_data.loc[dash_data.iso == extract_iso].copy()
    
    if not df['Doorstep conditions'].loc[(df['year'] == selected_year)& (df['iso'] == extract_iso)].empty:
        value = df['Doorstep conditions'].loc[(df['year'] == selected_year) & (df['iso'] == extract_iso)].values[0]
        formatted_value = '{:.2f}'.format(value)

        fig = px.line(df, x='year', y='Doorstep conditions')
        fig.update_layout(
                            title = {'text': f'Doorstep Condition Index',
                                    'y': 0.9,
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'yanchor': 'top',
                                    'font': {'size': 15}    
                                    },
                            showlegend=False, 
                            width=380, 
                            height=300, 
                                                    
                            xaxis=dict(
                                title=None,
                                dtick=10
                            ),
                            yaxis=dict(
                                title='',
                                showticklabels=True,
                                dtick=0.25,
                                range=[0,1],
                                ticktext=["0","0.25: Fragile", "0.5: Basic", "0.75: Mature","1"],  # Custom text labels for dticks
                                tickmode="array",  # Use custom ticktext
                                tickvals=[0, 0.25, 0.5, 0.75, 1]  # Corresponding values for dticks
                                ),
                            annotations=[
                            dict(
                                x=selected_year,
                                y=df.loc[df['year'] == selected_year, 'Doorstep conditions'].iloc[0],
                                xref='x',
                                yref='y',
                                text=str(formatted_value),
                                showarrow=True,
                                arrowhead=0,
                                ax=0,
                                ay=-40
                            )
                            ],
                        

                        )
    else:
        #pass
        fig = px.line(df, x='year', y='Doorstep conditions')
        fig.update_layout(
                            title = {'text': f'Doorstep Condition Index',
                                    'y': 0.9,
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'yanchor': 'top',
                                    'font': {'size': 15}    
                                    },
                            showlegend=False, 
                            width=380, 
                            height=300, 
                                                    
                            xaxis=dict(
                                title=None,
                                dtick=10
                            ),
                            yaxis=dict(
                                title='',
                                showticklabels=True,
                                dtick=0.25,
                                range=[0,1],
                                #ticktext=["0","0.25: Fragile", "0.5: Basic", "0.75: Mature","1"],  # Custom text labels for dticks
                                tickmode="array",  # Use custom ticktext
                                tickvals=[0, 0.25, 0.5, 0.75, 1]  # Corresponding values for dticks
                                ),
                            annotations=[
                            dict(
                                x=selected_year,
                                #y=df.loc[df['year'] == selected_year, 'Doorstep conditions'].iloc[0],
                                xref='x',
                                yref='y',
                                text='no data',
                                showarrow=True,
                                arrowhead=0,
                                ax=0,
                                ay=-40
                            )
                            ],
                        

                        )
    return(fig)


# 2.4 Line chart: Income Justice 


def ij_line_plot_func(extract_iso,selected_year):

    fig = None

    df=dash_data.loc[dash_data.iso == extract_iso].copy()
    
    if not df['Income justice'].loc[(df['year'] == selected_year)& (df['iso'] == extract_iso)].empty:
        value = df['Income justice'].loc[(df['year'] == selected_year) & (df['iso'] == extract_iso)].values[0]
        formatted_value = '{:.2f}'.format(value)

        fig = px.line(df, x='year', y='Income justice')
        fig.update_layout(
                            title = {'text': f'Income Justice Index',
                                    'y': 0.9,
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'yanchor': 'top',
                                    'font': {'size': 15}    
                                    },
                            showlegend=False, 
                            width=380, 
                            height=300, 
                                                    
                            xaxis=dict(
                                title=None,
                                dtick=10
                            ),
                            yaxis=dict(
                                title='',
                                showticklabels=True,
                                dtick=0.25,
                                range=[0,1],
                                ticktext=["0","0.25", "0.5", "0.75","1"],  # Custom text labels for dticks
                                tickmode="array",  # Use custom ticktext
                                tickvals=[0, 0.25, 0.5, 0.75, 1]  # Corresponding values for dticks
                                ),
                            annotations=[
                            dict(
                                x=selected_year,
                                y=df.loc[df['year'] == selected_year, 'Income justice'].iloc[0],
                                xref='x',
                                yref='y',
                                text=str(formatted_value),
                                showarrow=True,
                                arrowhead=0,
                                ax=0,
                                ay=-40
                            )
                            ],
                        

                        )
    else:
        fig = px.line(df, x='year', y='Income justice')
        fig.update_layout(
                            title = {'text': f'Income Justice Index',
                                    'y': 0.9,
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'yanchor': 'top',
                                    'font': {'size': 15}    
                                    },
                            showlegend=False, 
                            width=380, 
                            height=300, 
                                                    
                            xaxis=dict(
                                title=None,
                                dtick=10
                            ),
                            yaxis=dict(
                                title='',
                                showticklabels=True,
                                dtick=0.25,
                                range=[0,1],
                                ticktext=["0","0.25", "0.5", "0.75","1"],  # Custom text labels for dticks
                                tickmode="array",  # Use custom ticktext
                                tickvals=[0, 0.25, 0.5, 0.75, 1]  # Corresponding values for dticks
                                ),
                            annotations=[
                            dict(
                                x=selected_year,
                                #y=df.loc[df['year'] == selected_year, 'Income justice'].iloc[0],
                                xref='x',
                                yref='y',
                                text='no data',
                                showarrow=True,
                                arrowhead=0,
                                ax=0,
                                ay=-40
                            )
                            ],
                        

                        )


    return(fig)

# 3. Dash app

# Dash app

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])  # LUX was ok, try SLATE, DARKLY
server = app.server
# Components

mytitle = dcc.Markdown('Asian Development Dashboard (BETA)', id='main_title', style={'font-size': '48px', 'font-weight': 'bold', 'text-align': 'center'})

subheader = dcc.Markdown('', id='sub_header', style={'font-size': '36px', 'text-align': 'center'})

dropdown = dcc.Dropdown(id='feature_dropdown', 
                        options = dash_data.columns.values[6:12],
                        value='Doorstep conditions',  # initial value displayed when page first loads
                        clearable=False)

map_graph = dcc.Graph(id='choropleth_map',figure=choropleth_plot_func(1978)) #, clickData={}

year_range = range(dash_data['year'].min(),dash_data['year'].max())
year_slider =dcc.Slider(
                    id='year_slider',
                    min=dash_data['year'].min(),
                    max=dash_data['year'].max(),
                    value=1975,
                    marks={str(year):{'label':str(year),'style':{'transform': 'rotate(45deg)'}} for year in year_range[::5]},
                    #marks={each: {"label": str(year), 'style':{'transform': 'rotate(45deg)'}} for each, year in enumerate(dash_data['year'].unique())},#range(1975, 2015)}, #, 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'
                    step=1,
                    updatemode='drag'
                    )

radar_chart = dcc.Graph(id='radar_chart', 
                        figure=radar_plot_func('', 0),
                        clickData=None, 
                        hoverData=None)

dc_line_chart = dcc.Graph(id='doorstep_line_chart', figure=dc_line_plot_func('IDN',1975))
ij_line_chart = dcc.Graph(id='income_justice_line_chart', figure=ij_line_plot_func('IDN',1975))

bar_chart = dcc.Graph(id='bar_chart', figure={}, 
                    clickData=None,
                    hoverData=None)



# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([mytitle], width={"size":"8","offset":1}, style={'height': '80px'})
    ], justify='center'),
    
    dbc.Row([
        dbc.Col([subheader], width={"size":"8"}, style={'height': '40px'})
    ], justify='center'),
    

    dbc.Row([
        dbc.Col([map_graph], width='auto'),
        dbc.Col([radar_chart], width='auto'),
        ], justify='center', align='center'),

    dbc.Row([
    #    dbc.Col([dropdown], width=6),
        dbc.Col([year_slider], align='start', width={"size":"4","offset":2})    
            ], justify='start'),

    dbc.Row([
        dbc.Col([dc_line_chart], width={"size":"3","offset":1}), 
        dbc.Col([ij_line_chart], width={"size":"3"}),
        dbc.Col([bar_chart], width={"size":"3", "offset":0}) 
    
    ], align='start'),

], fluid=True)



# 1. Callback: Update choropleth from year slider

@app.callback(
    Output('choropleth_map', 'figure'),
    Input('year_slider', 'value')
)
def update_choropleth_plot(selected_year):
    fig = choropleth_plot_func(selected_year)
    return (fig)


# 2. Callback: Select country from choropleth for radar and line charts

@app.callback(
    Output('doorstep_line_chart', 'figure'),
    Output('income_justice_line_chart', 'figure'),
    Output('radar_chart', 'figure'),
    Output('sub_header','children'),
    Input('year_slider', 'value'),
    Input('choropleth_map', 'clickData')
    )

def hover_polar_func(selected_year, map_click_dict):
    if map_click_dict is None:
        fig_radar = radar_plot_func('IDN', selected_year)
        fig_dc_line = dc_line_plot_func('IDN',selected_year)
        fig_ij_line = ij_line_plot_func('IDN',selected_year)
        markdown_subheader = f'Indonesia in {selected_year}' 
        return(fig_dc_line,fig_ij_line,fig_radar,markdown_subheader)
    
    else:
        extract_iso = map_click_dict['points'][0]['location']
        extract_country = map_click_dict['points'][0]['text']
        fig_radar = radar_plot_func(extract_iso, selected_year) 
        fig_dc_line = dc_line_plot_func(extract_iso, selected_year)
        fig_ij_line = ij_line_plot_func(extract_iso,selected_year)
        markdown_subheader = f'{extract_country} in {selected_year}'
        return(fig_dc_line,fig_ij_line, fig_radar, markdown_subheader)
    


# 2. Callback: HoverPolar - Bar plot

@app.callback(
    Output('bar_chart', 'figure'),
    Input('year_slider', 'value'),
    Input('choropleth_map', 'clickData'),
    Input('radar_chart', 'hoverData'),
    
            )

def update_bar_chart(selected_year, map_click_dict, radar_hover_dict):    
    if radar_hover_dict is None and map_click_dict is None: 
        fig_bar = plot_dc_bar('Legitimacy', 'IDN', selected_year)
    elif radar_hover_dict is None and map_click_dict is not None:
        extract_iso = map_click_dict['points'][0]['location']
        fig_bar = plot_dc_bar('Legitimacy', extract_iso, selected_year)
    else:
        extract_dc = radar_hover_dict['points'][0]['theta']
        extract_iso = map_click_dict['points'][0]['location']
  
        fig_bar = plot_dc_bar(extract_dc, extract_iso, selected_year)  
    return(fig_bar)  

# Run app
if __name__=='__main__':
    app.run_server()  
    
