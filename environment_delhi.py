# Import packages
import dash
import dash_daq
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import json
import pandas as pd
import geopandas as gpd
from dash.dependencies import Input, Output
from common import *

import folium
from folium.plugins import MarkerCluster, FastMarkerCluster
from folium import plugins
from folium.plugins import HeatMap

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

from datetime import datetime as dt
import jenkspy

# FUNCTIONS THAT'LL BE USED
def get_geojson_grid(upper_right, lower_left, lat_res = 0.008993300000000204, lon_res = 0.0096989, km_res=1):

    all_boxes = []
    lat_steps = np.arange(lower_left[0], upper_right[0], lat_res*km_res)
    lon_steps = np.arange(lower_left[1], upper_right[1], lon_res*km_res)

    lat_stride = lat_steps[1] - lat_steps[0]
    lon_stride = lon_steps[1] - lon_steps[0]

    for lat in lat_steps[:-1]:
        for lon in lon_steps[:-1]:
            # Define dimensions of box in grid
            upper_left = [lon, lat + lat_stride]
            upper_right = [lon + lon_stride, lat + lat_stride]
            lower_right = [lon + lon_stride, lat]
            lower_left = [lon, lat]

            # Define json coordinates for polygon
            coordinates = [
                upper_left,
                upper_right,
                lower_right,
                lower_left,
                upper_left
            ]

            geo_json = {"type": "FeatureCollection",
                        "properties":{
                            "lower_left": lower_left,
                            "upper_right": upper_right
                        },
                        "features":[]}

            grid_feature = {
                "type":"Feature",
                "geometry":{
                    "type":"Polygon",
                    "coordinates": [coordinates],
                }
            }

            geo_json["features"].append(grid_feature)

            all_boxes.append(geo_json)

    return all_boxes

# Datasets
f = open("data/delhi.geojson", "r")
delhi_geojson = json.load(f)
f2 = open("data/delhi_ac.geojson", "r")
delhi_ac_geojson = json.load(f2)
delhi_ac_gdf = gpd.read_file('data/delhi_ac.geojson')
f3 = open("data/Delhi_Wards.geojson", "r")
delhi_wards_gdf = gpd.read_file("data/Delhi_Wards.geojson")
delhi_wards_geojson = json.load(f3)

df = pd.read_csv("data/Environ_RawData.csv", encoding='latin1')
#df.index = pd.to_datetime(df['Date and Time'])
df['Date'] = df['Month'].astype(str) + '/' + df['Year'].astype(str)
df.index = pd.to_datetime(df['Date and Time']).dt.date
df.index = pd.to_datetime(df.index)
df = df.sort_index()

# external_stylesheets1 = [
#     {
#         'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
#         'rel': 'stylesheet',
#         'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
#         'crossorigin': 'anonymous'
#     }, {
#         dbc.themes.SUPERHERO
#     }
# ]

#APP
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])
server = app.server

callback = """
function (row) {
    var icon, marker;
    icon = L.AwesomeMarkers.icon({
        icon: "map-marker", markerColor: "red"});
    marker = L.marker(new L.LatLng(row[0], row[1]));
    marker.setIcon(icon);

    return marker;
};
"""

# Side-Menu
side_page_menu = []

side_page_menu.append(
    # html.Div(className='', children=[
    #     html.Div( className="side_menu_option", children=[
    #         html.I(className="fa fa-camera-retro fa-lg")
    #     ]),
    #      html.Div( className="side_menu_option", children=[
    #         html.I(className="fa fa-camera-retro fa-lg")
    #     ])

    # ]
    # )
    # html.Div(className="area"),
    html.Nav(className="main-menu" ,children=[
        html.Ul(children=[
            html.Li(children=[
                html.I(className="fa fa-home fa-lg"),
                #html.Span("Home",className="nav-text")
                dbc.NavLink("Home",href="/",active="exact")
            ]),
            html.Li(children=[
                html.I(className="fa fa-camera-retro fa-lg"),
                #html.Span("Dashboard",className="nav-text")
                dbc.NavLink("Dashboard",href="/app1",active="exact")
            ])
        ])
    ])
)

# add filters here
filters = []

filters.append(
    html.Div(className="filters", children=[
        html.Div(className='SmallHeader', children=[
            html.H6('Time Period')
        ]
        ),
    dcc.DatePickerRange(
        id='date-picker-range',
        calendar_orientation='horizontal',
        day_size=39,
        #end_date_placeholder_text="Return",
        with_portal=True,
        first_day_of_week=1,
        reopen_calendar_on_clear=True,
        is_RTL=False,
        clearable=True,
        number_of_months_shown=1,
        min_date_allowed=df.index.min(),
        max_date_allowed=df.index.max(),
        initial_visible_month=dt(2020,11,1),
        start_date=dt(2020,11,1).date(),
        end_date=dt(2020,11,30).date(),
        display_format='MMM Do, YY',
        month_format='MMMM, YYYY',
        minimum_nights=2,

        persistence = True,
        persisted_props=['start_date','end_date'],

        updatemode='singledate'
    )]
    )

)

filters.append(
    html.Div(className="filters", children=[
        html.Div(className='SmallHeader', children=[
            html.H6('Resolution (in sq.km)')
        ]
        ),
        dash_daq.NumericInput(
        id='my-numeric-input',
        value=10
    )
    ]
             )
)

filters.append(
    html.Div(className="filters", children=[
        html.Div(className='SmallHeader', children=[
            html.H6('Department')
        ]
        ),
        dcc.Dropdown(
            id="Department",
            options=[{'label': i, 'value': i}
                     for i in df['Department Name'].unique()],
            value=None,
            multi=False,
            clearable=True,
            searchable=True,
            placeholder='Select Department'
        ),
    ]
)
)



filters.append(
    html.Div(className="filters", children=[
        html.Div(className='SmallHeader', children=[
            html.H6('Offences')
        ]
        ),
        dcc.Dropdown(
            id="Offences",
            options=[{'label': i, 'value': i} for i in df.Offences.unique()],
            value='Illegal dumping of Garbage on road sides/ vacant land',
            #labelStyle={'font-size': '.7em','color': 'black'},
            placeholder="Select Offence",
            multi=False,
            searchable=True,
            clearable=True,
        ),
    ]
    )
)

filters.append(
    html.Div(className="filters-end", children=[])
)

# Actual content on the right side. Append each row one by one.
right_content= []

right_content.append(
    html.Div(className="row margin1", children=[
        html.Div(className="col-md-12 chart_container", children=[
            html.H4('Choropleth Map for selected grievances'),
            html.Iframe(id='choropleth-map', srcDoc=None, width='95%', height='500')
             ])
    ])
)


right_content.append(
    html.Div(className="row margin1", children=[
        html.Div(className="col-md-12 chart_container", children=[
            html.H4('Grid Map for selected grievances'),
            html.Iframe(id='grid-map', srcDoc=None, width='95%', height='500')
             ])
    ])
)

right_content.append(
    html.Div(className="row margin1", children=[
        html.Div(className="col-md-12 chart_container", children=[
            html.H4('Cluster map for the selected grievance'),
            html.Iframe(id='heat-map', srcDoc=None, width='95%', height='500')
             ])
    ]),
)

# APP LAYOUT
app.layout = getLayout(app, filters, side_page_menu, right_content)

# CALLBACKS -- FILTERS

# Callback for Offence Options
@app.callback(
    Output('Offences', 'options'),
    [Input('Department', 'value')]
)
def get_offence_options(department):
    if department is not None:
        return [{'label': i, 'value': i} for i in df[df['Department Name'] == department].Offences.unique()]
    else:
        return [{'label': i, 'value': i} for i in df.Offences.unique()]


# Callback for Offence Values
@app.callback(
    Output('Offences', 'value'),
    [Input('Offences', 'options')]
)
def get_variety_values(offences):
    return 'Illegal dumping of Garbage on road sides/ vacant land'

# CALLBACKS - RIGHT CONTENT
@app.callback(
    [Output('choropleth-map', 'srcDoc'),
     Output('grid-map', 'srcDoc'),
     Output('heat-map', 'srcDoc')],
    [Input('Department', 'value'),
     Input('Offences', 'value'),
     Input('date-picker-range', 'start_date'), Input('date-picker-range', 'end_date'),
     Input('my-numeric-input', 'value')]
)
def get_heatmap(department, offencelist, start_date, end_date, kmres):
    radius = 10
    centre_lat = 28.7041
    centre_lon = 77.1025

    ## PREPARE REQUIRED FILTERED DATA
    ggg = df.copy()
    polygons_wards = delhi_wards_gdf.copy()
    polygons_acs = delhi_ac_gdf.copy()

    df_c = ggg.loc[str(start_date):str(end_date)]
    if department is not None:
        df_c = df_c[df_c['Department Name'] == department].reset_index(drop=True)
    else:
        df_c = df_c
    df_c = df_c[df_c['Offences'] == offencelist].reset_index(drop=True)

    gdf = gpd.GeoDataFrame(df_c,
                           geometry=gpd.points_from_xy(df_c.Longitude, df_c.Latitude)
                           ).reset_index(drop=True)
    points = gpd.GeoDataFrame(gdf.copy())

    # Ensure you're handing it floats
    df_c['Latitude'] = df_c['Latitude'].astype(float)
    df_c['Longitude'] = df_c['Longitude'].astype(float)

    # MAPS

    ## Choropleths
    # Spatial Joins - Wards
    pointsInWards = gpd.sjoin(points.set_crs('epsg:4326'), polygons_wards, how="inner", op='intersects')

    pointsInWards = pointsInWards.groupby('Ward_Name')[['index']].count().reset_index()
    pointsInWards.columns = ['Ward_Name', 'NumberofComplaints']

    # Spatial Joins - ACs
    pointsInACs = gpd.sjoin(points.set_crs('epsg:4326'), polygons_acs, how="inner", op='intersects')

    pointsInACs = pointsInACs.groupby('AC_NAME')[['PC_ID']].count().reset_index()
    pointsInACs.columns = ['AC_NAME', 'NumberofComplaints']

    polygons_wards = polygons_wards.merge(pointsInWards, on='Ward_Name', how='left').fillna(0).sort_values(
        by='NumberofComplaints', ascending=False)
    polygons_acs = polygons_acs.merge(pointsInACs, on='AC_NAME', how='left').fillna(0).sort_values(
        by='NumberofComplaints', ascending=False)

    breaks_wards = jenkspy.jenks_breaks(polygons_wards['NumberofComplaints'], nb_class=5)
    breaks_acs = jenkspy.jenks_breaks(polygons_acs['NumberofComplaints'], nb_class=5)

    m = folium.Map(location=[centre_lat, centre_lon],
                   zoom_start=10, tiles="OpenStreetMap")

    ward_choropleth = folium.Choropleth(
        geo_data=polygons_wards,
        name="Ward_choropleth",
        data=polygons_wards,
        columns=["Ward_Name", "NumberofComplaints"],
        key_on='feature.properties.Ward_Name',
        fill_Color='OrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Number of Complaints",
        bins=breaks_wards,  # Natural Breaks
        highlight=True
    ).add_to(m)

    ward_choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=['Ward_Name', 'NumberofComplaints'],
            aliases=['Ward:', 'Number of Complaints:'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")))

    ac_choropleth = folium.Choropleth(
        geo_data=polygons_acs,
        name="AC_choropleth",
        data=polygons_acs,
        columns=["AC_NAME", "NumberofComplaints"],
        key_on='feature.properties.AC_NAME',
        fill_Color='OrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Number of Complaints",
        bins=breaks_acs,  # Natural Breaks,
        show=False,
        highlight=True
    ).add_to(m)

    ac_choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=['AC_NAME', 'NumberofComplaints'],
            aliases=['Assembly:', 'Number of Complaints:'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")))

    folium.LayerControl('topright', collapsed=True).add_to(m)

    m.save("Choropleth.html")

    ### Full map - clusters
    map_hooray2 = folium.Map(location=[centre_lat, centre_lon],
                             zoom_start=10)
    # Filter the DF for rows, then columns, then remove NaNs
    heat_df = df_c[['Latitude', 'Longitude']]
    heat_df = heat_df.dropna(axis=0, subset=['Latitude', 'Longitude'])

    # List comprehension to make out list of lists
    heat_data = [[row['Latitude'], row['Longitude']] for index, row in heat_df.iterrows()]

    # Plot HeatMap on the map
    HeatMap(heat_data, name="HeatMap", radius=radius, min_opacity=0.7, max_opacity=1,gradient={0.4:"green", 0.6:"yellow", 1:"red"}, blur=6).add_to(map_hooray2)

    folium.GeoJson(delhi_geojson, name='district_map',
                   style_function=lambda x: {
                       'color': 'black',
                       'weight': 4,
                       "opacity": 1,
                       'fillOpacity': 0,
                       'interactive': False
                   }).add_to(map_hooray2)

    folium.GeoJson(delhi_ac_geojson, name='Assembly_map', show=False,
                   style_function=lambda x: {
                       'color': 'black',
                       'weight': 4,
                       "opacity": 1,
                       'fillOpacity': 0,
                       'interactive': False
                   }).add_to(map_hooray2)

    folium.GeoJson(delhi_wards_geojson, name='Wards_map', show=False,
                   style_function=lambda x: {
                       'color': 'black',
                       'weight': 4,
                       "opacity": 1,
                       'fillOpacity': 0,
                       'interactive': False
                   }).add_to(map_hooray2)

    # Plot Marker-CLusters on the map
    locations = list(zip(df_c["Latitude"], df_c["Longitude"]))
    # popups = ["lon:{}<br>lat:{}".format(lon, lat) for (lat, lon) in locations]
    marker_cluster = FastMarkerCluster(locations,
                                       name='ClusterMap',
                                       control=True,
                                       callback=callback)
    marker_cluster.add_to(map_hooray2)

    folium.LayerControl().add_to(map_hooray2)

    # Display the map
    map_hooray2.save("Delhi_HeatMap_Cluster.html")

    # Grid Map
    top_left = [28.41387, 76.83753]
    top_right = [28.88525, 77.33561]
    grid = get_geojson_grid(top_right, top_left, km_res=kmres)
    # Calculate count per grid
    regional_counts = []
    tooltips = []

    for box in grid:
        upper_right = box["properties"]["upper_right"]
        lower_left = box["properties"]["lower_left"]

        mask = (
                (df_c.Latitude <= upper_right[1]) & (df_c.Latitude >= lower_left[1]) &
                (df_c.Longitude <= upper_right[0]) & (df_c.Longitude >= lower_left[0])
        )

        region_incidents = len(df_c[mask])
        regional_counts.append(region_incidents)

        # total_vehicles = df[mask].Number_of_Vehicles.sum()
        # total_casualties = df[mask].Number_of_Casualties.sum()
        content = "Total complaints: {:,.0f}".format(region_incidents)
        tooltip = folium.Tooltip(content)
        tooltips.append(tooltip)

    worst_region = max(regional_counts)

    m = folium.Map(location=[centre_lat, centre_lon],
                   zoom_start=10)

    #If worst region is 0 (which happens when you don't select offence / when no offence registered ) - Need a popup
    if worst_region==0:
        m.save("empty.html")
        return open('empty.html', 'r').read(), open('empty.html', 'r').read()

    # Add GeoJson to map
    for i, box in enumerate(grid):
        geo_json = json.dumps(box)

        color = plt.cm.Reds(regional_counts[i] / worst_region)
        color = mpl.colors.to_hex(color)

        gj = folium.GeoJson(geo_json,
                            style_function=lambda feature,
                                                  color=color: {
                                'fillColor': color,
                                'color': "black",
                                'weight': 1,
                                'dashArray': '5, 5',
                                'fillOpacity': 0.55,
                            })

        gj.add_child(tooltips[i])
        m.add_child(gj)
        m.add_child(marker_cluster)
        #folium.LayerControl().add_to(m)
        m.save("Delhi_HeatMap_Grid.html")

    return open('Choropleth.html').read(), open('Delhi_HeatMap_Grid.html', 'r').read(), open('Delhi_HeatMap_Cluster.html', 'r').read()


if __name__ =='__main__':
    app.run_server(debug=True, use_reloader=False)