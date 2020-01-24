
# We will use plot-ly heavily for our graphics
import plotly.graph_objects as go
import plotly.subplots as subplots

# Define some useful interactive 3D plotting
# Note that this can be very memory intensive!!
#
# Also note that the plotting package we aer using is is plot-ly
#
# In the first we define simply a heat map stuly event display
def plotEventView2D(waveforms):
    # Create figure
    fig = go.Figure()
    
    # Add surface trace
    fig.add_trace(go.Heatmap(z=waveforms, colorscale="Greys"))
    
    # Update plot sizing
    fig.update_layout(
        width=800,
        height=900,
        autosize=False,
        margin=dict(t=100, b=0, l=0, r=0),
    )
    
    # Update 3D scene options
    fig.update_scenes(
        aspectratio=dict(x=1, y=1, z=0.7),
        aspectmode="manual"
    )
    
    # Add drowdowns
    button_layer_1_height = 1.08
    fig.update_layout(
        updatemenus=[
            go.layout.Updatemenu(
                buttons=list([
                    dict(
                        args=["colorscale", "Viridis"],
                        label="Viridis",
                        method="restyle"
                    ),
                    dict(
                        args=["colorscale", "Cividis"],
                        label="Cividis",
                        method="restyle"
                    ),
                    dict(
                        args=["colorscale", "Blues"],
                        label="Blues",
                        method="restyle"
                    ),
                    dict(
                        args=["colorscale", "Greys"],
                        label="Greys",
                        method="restyle"
                    ),
                ]),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top"
            ),
            go.layout.Updatemenu(
                buttons=list([
                    dict(
                        args=["reversescale", False],
                        label="False",
                        method="restyle"
                    ),
                    dict(
                        args=["reversescale", True],
                        label="True",
                        method="restyle"
                    )
                ]),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.37,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top"
            ),
            #go.layout.Updatemenu(
            #    buttons=list([
            #        dict(
            #            args=[{"contours.showlines": False, "type": "contour"}],
            #            label="Hide lines",
            #            method="restyle"
            #        ),
            #        dict(
            #            args=[{"contours.showlines": True, "type": "contour"}],
            #            label="Show lines",
            #            method="restyle"
            #        ),
            #    ]),
            #    direction="down",
            #    pad={"r": 10, "t": 10},
            #    showactive=True,
            #    x=0.58,
            #    xanchor="left",
            #    y=button_layer_1_height,
            #    yanchor="top"
            #),
        ]
    )
    
    fig.update_layout(
        annotations=[
            go.layout.Annotation(text="colorscale", x=0, xref="paper", y=1.06, yref="paper",
                                 align="left", showarrow=False),
            go.layout.Annotation(text="Reverse<br>Colorscale", x=0.25, xref="paper", y=1.07,
                                 yref="paper", showarrow=False),
            go.layout.Annotation(text="Lines", x=0.54, xref="paper", y=1.06, yref="paper",
                                 showarrow=False)
        ])
    
    #fig.show()
    
    return fig



# This is a more fancy 3D rendering of an event display
def plotEventView3D(waveforms):
    particleFig = go.Figure()
    
    particleFig.add_trace(go.Heatmap(z=waveforms, colorscale="Greys"))
    
    
    # Update plot sizing
    particleFig.update_layout(
        width=800,
        height=800,
        autosize=False,
        margin=dict(t=0, b=0, l=0, r=0),
        template="plotly_white",
    )
    
    # Update 3D scene options
    particleFig.update_scenes(
        aspectratio=dict(x=1, y=1, z=0.7),
        aspectmode="manual"
    )
    
    # Add dropdown
    particleFig.update_layout(
        updatemenus=[
            go.layout.Updatemenu(
                buttons=list([
                    dict(
                        args=["colorscale", "Greys"],
                        label="Greys",
                        method="restyle"
                    ),
                    dict(
                        args=["colorscale", "Viridis"],
                        label="Viridis",
                        method="restyle"
                    ),
                    dict(
                        args=["colorscale", "Cividis"],
                        label="Cividis",
                        method="restyle"
                    ),
                    dict(
                        args=["colorscale", "Blues"],
                        label="Blues",
                        method="restyle"
                    )
                ]),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.1,
                yanchor="top"
            ),
            go.layout.Updatemenu(
                buttons=list([
                    dict(
                        args=["type", "heatmap"],
                        label="Heatmap",
                        method="restyle"
                    ),
                    dict(
                        args=["type", "surface"],
                        label="3D Surface",
                        method="restyle"
                    )
                ]),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.37,
                xanchor="left",
                y=1.1,
                yanchor="top"
            ),
        ]
    )
    
    # Add annotation
    particleFig.update_layout(
        annotations=[
            go.layout.Annotation(text="colorscale", x=0, xref="paper", y=1.06, yref="paper",
                                 align="left", showarrow=False),
            go.layout.Annotation(text="Trace Type", x=0.25, xref="paper", y=1.06,
                                 yref="paper", showarrow=False)
#            go.layout.Annotation(text="Trace type:", showarrow=False,
#                                 x=0, y=1.085, yref="paper", align="left")
        ]
    )
    
    #particleFig.show()

    return particleFig


