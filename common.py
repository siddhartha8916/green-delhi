import dash_html_components as html

def getHeader(app):
    return html.Div(
        children=[
            html.Div(
                className="row margin1",
                children=[
                    html.Div(
                        className="col-md-10",
                        style={'float': 'left','border-bottom':'solid 1px #E1E1E1'},
                        children=[
                            html.H3( 'Green Delhi Grievance Analytics', className="solid-bottom"),
                            html.H5('GIS mapping of complaints received through Green Delhi app')
                        ]
                    ),
                    html.Div(
                        className="col-md-2",
                        style={'border-bottom':'solid 1px #E1E1E1'},
                        # style={'float': 'right'},
                        children=[
                            html.A(
                                html.Img(
                                    src=app.get_asset_url(
                                        "gdi-high-logo.png"),
                                    style={
                                        'float': 'right', 'height': '50px', 'margin-top': '1.5rem'}
                                ),
                                href="https://gdipartners.in/"
                            ),
                        ]
                    )
                ]
            )
        ]
    )


def getLayout(app, filters, side_page_menu, right_content):
    header = getHeader(app)
    div = html.Div(
        className='app-body',
        children=[
            # Stores

            # ROW - About the App + Logo
            html.Div(className="header-content",
                     children=[
                         html.Div(header)
                     ]
                     ),

            # 2ndROW - contains left menu and all the right content,
            # Do not need to change this. Add content above in right_content
            html.Div(
                className="row",
                # id="control-panel",
                children=[
                    html.Div(className="col-md-2 navbar-fixed-left", id="", children=[
                        html.Div(className="row", children=[
                            html.Div(className="col-md-1", children=[
                                html.Div(side_page_menu)]
                            ),
                            html.Div(className="col-md-10", id="control-panel", children=[
                                html.Div(filters)]
                            )
                        ]),
                    ]),
                    html.Div(className="col-md-2", children=[
                        # this is required as left columns are fixed
                    ]),
                    html.Div(className="col-md-10", children=[
                        html.Div(right_content)
                    ]),
                ]
            ),
        ]
    )
    return div