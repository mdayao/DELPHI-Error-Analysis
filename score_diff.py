import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import plotly
import plotly.graph_objects as go

import os
import tkinter
root = tkinter.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

#--------------------------------------------------------------------------#
# MODIFY THESE AS NEEDED

# The directory where your score files are located
score_directory = '../Delphi 2018/natreg/'

# The score difference that is plot will be calculated by (second_file - first_file).
# Therefore, a negative score difference indicates that the second model performed worse than the first model.

# Specify your score files here:
first_filename = 'LANL-Dante.csv'
second_filename = 'Delphi-Epicast2.csv'

# Do you want the dropdown menu to contain targets or regions? If targets, set to True. Otherwise, set to False.
dropdown_targets = True

# Specify the name of the output html file:
# output_file = 'compare_regions.html'
output_file = 'compare_targets.html'

# This script assumes the 2018 format for the score files. The plot also prints
# If you want to use score files from a different season, you may need to adjust some of the parameters below.
# (look for comments that say "assumes 2018 format")

#--------------------------------------------------------------------------#

# assumes 2018 format
locations = np.concatenate((['US National'],['HHS Region %i' %i for i in range(1,11)]))
targets = np.array(['Season onset', 'Season peak week', 'Season peak percentage', '1 wk ahead', '2 wk ahead', '3 wk ahead', '4 wk ahead'])

num_locations = len(locations)
num_targets = len(targets)

c_filename_woext = os.path.splitext(first_filename)[0]
d_filename_woext = os.path.splitext(second_filename)[0]

compare_file = pd.read_csv(score_directory + first_filename)
second_file = pd.read_csv(score_directory + second_filename)

comp_weeks = compare_file.competition_week.unique()

second_file_no_dup = second_file.drop_duplicates()
second_file_sorted = second_file_no_dup.sort_values(['location', 'target', 'competition_week']) # assumes 2018 format

c_file_no_dup = compare_file.drop_duplicates()
c_file_sorted = c_file_no_dup.sort_values(['location', 'target', 'competition_week']) # assumes 2018 format

diff_file = second_file_sorted.copy()

diff_file['score'] = second_file_sorted['score'] - c_file_sorted['score']

if dropdown_targets:

    targets_avg_diff_file = diff_file.groupby(['location','competition_week']).mean().reset_index() # assumes 2018 format
    # Targets in dropdown menu
    data = []
    for target in targets:
        for location in locations:
            trace = go.Scatter(x=diff_file[(diff_file.location == location) & (diff_file.target == target)].competition_week,
                        y=diff_file[(diff_file.location == location) & (diff_file.target == target)].score,
                        name=location)
            data.append(trace)
            
    for location in locations:
        trace_avg_targets = go.Scatter(x=targets_avg_diff_file[(targets_avg_diff_file.location == location)].competition_week,
                                    y=targets_avg_diff_file[(targets_avg_diff_file.location == location)].score,
                                    name=location)
        data.append(trace_avg_targets)

    data_to_show = [False] * len(data)

    button_list = [
    dict(label = targets[t],method = "update",
        args = [{"visible": [True if i in range(t*num_locations,(t+1)*num_locations) else data_to_show[i] for i in range(len(data))]},
                ])
    for t in range(num_targets)
    ]
    button_list.append(dict(label = 'Average',method = "update",
                    args = [{"visible": [True if i in range((num_targets)*num_locations,(num_targets+1)*num_locations) else data_to_show[i] for i in range(len(data))]},
                            ]))
    updatemenus = list([
        dict(active=-1,
            buttons=list(button_list)
        ),
    ])
    annotation_text = 'To get started, select an option from the dropdown menu above. You can select plots by target, or the average over all targets. <br><br>This plot shows the difference in log score between ' + d_filename_woext + ' and ' + c_filename_woext + ' for the 2018/19 season. <br><br>The difference value is the (' + d_filename_woext + ') - (' + c_filename_woext + ') score, so the more negative the value is, the worse the <br>' + d_filename_woext + ' model scored compared to ' + c_filename_woext + '. <br><br>There are various tools in the top right of this screen that allow you to pan, zoom, etc. <br>By double-clicking on a option in the legend on the right side of the page, you can isolate just one curve in the plot. <br>Double-clicking again will restore the rest of the curves.'
    layout = dict(title="Difference in Log Score between " + d_filename_woext + " and " + c_filename_woext + ', 2018 ',
                #   xaxis=dict(title="Competition Week"), # uncomment if you want to show competition weeks instead of epiweeks
                yaxis=dict(title="Difference in Log Score"),
                updatemenus=updatemenus,
                xaxis=dict(tickmode='array',
                    tickvals=[j for j in range(1,len(comp_weeks)+1)],
                    ticktext=[str(i-11) if i > 11 else str(i + 41) for i in range(1,len(comp_weeks)+1)], # assumes 2018 format
                            title="Forecast Week (Epiweek)"),
                annotations=[
                    go.layout.Annotation(
                            x=-.09,
                            y=1.08,
                            xref="paper",
                            yref="paper",
                            text='(scroll down for more information)', 
                            xanchor='center',
                            yanchor='top',
                            ax=0,
                            ay=0,
                            align='left'
                            ),
                    go.layout.Annotation(
                            x=.4,
                            y=-.5,
                            xref="paper",
                            yref="paper",
                            text=annotation_text, 
                            xanchor='center',
                            yanchor='bottom',
                            ax=0,
                            ay=0,
                            align='left'
                            ),
                    ],
                    # autosize = False,
                    height = screen_height + 800,
                    margin=go.layout.Margin(
                        l=50,
                        r=50,
                        b=1000,
                        t=100,
                        pad=4
        )      
                )
    fig = go.Figure(
        data = data,
        layout = layout
    )
    fig.update_xaxes(range=[comp_weeks.min(), comp_weeks.max()])

else: # regions in dropdown menu

    locations_avg_diff_file = diff_file.groupby(['target','competition_week']).mean().reset_index() # assumes 2018 format
    data = []
    for location in locations:
        for target in targets:
            trace = go.Scatter(x=diff_file[(diff_file.location == location) & (diff_file.target == target)].competition_week,
                        y=diff_file[(diff_file.location == location) & (diff_file.target == target)].score,
                        name=target)
            data.append(trace)
    for target in targets:
        trace_avg_locations = go.Scatter(x=locations_avg_diff_file[(locations_avg_diff_file.target == target)].competition_week,
                                    y=locations_avg_diff_file[(locations_avg_diff_file.target == target)].score,
                                    name=target)
        data.append(trace_avg_locations)

    data_to_show = [False] * len(data)

    button_list = [
    dict(label = locations[l],method = "update",
        args = [{"visible": [True if i in range(l*num_targets,(l+1)*num_targets) else data_to_show[i] for i in range(len(data))]},
                ])
    for l in range(num_locations)
    ]
    button_list.append(dict(label = 'Average',method = "update",
                    args = [{"visible": [True if i in range((num_locations)*num_targets,(num_locations+1)*num_targets) else data_to_show[i] for i in range(len(data))]},
                            ]))
    updatemenus = list([
        dict(active=-1,
            buttons=list(button_list)
        ),
    ])
    annotation_text = 'To get started, select an option from the dropdown menu above. You can select plots by target, or the average over all targets. <br><br>This plot shows the difference in log score between ' + d_filename_woext + ' and ' + c_filename_woext + ' for the 2018/19 season. <br><br>The difference value is the (' + d_filename_woext + ') - (' + c_filename_woext + ') score, so the more negative the value is, the worse the <br>' + d_filename_woext + ' model scored compared to ' + c_filename_woext + '. <br><br>There are various tools in the top right of this screen that allow you to pan, zoom, etc. <br>By double-clicking on a option in the legend on the right side of the page, you can isolate just one curve in the plot. <br>Double-clicking again will restore the rest of the curves.'
    layout = dict(title="Difference in Log Score between " + d_filename_woext + " and " + c_filename_woext + ', 2018 ',
                #   xaxis=dict(title="Competition Week"), # uncomment if you want to show competition weeks instead of epiweeks
                yaxis=dict(title="Difference in Log Score"),
                updatemenus=updatemenus,
                xaxis=dict(tickmode='array',
                    tickvals=[j for j in range(1,len(comp_weeks)+1)],
                    ticktext=[str(i-11) if i > 11 else str(i + 41) for i in range(1,len(comp_weeks)+1)], # assumes 2018 format
                            title="Forecast Week (Epiweek)"),
                annotations=[
                    go.layout.Annotation(
                            x=-.09,
                            y=1.08,
                            xref="paper",
                            yref="paper",
                            text='(scroll down for more information)', 
                            xanchor='center',
                            yanchor='top',
                            ax=0,
                            ay=0,
                            align='left'
                            ),
                    go.layout.Annotation(
                            x=.4,
                            y=-.5,
                            xref="paper",
                            yref="paper",
                            text=annotation_text, 
                            xanchor='center',
                            yanchor='bottom',
                            ax=0,
                            ay=0,
                            align='left'
                            ),
                    ],
                    # autosize = False,
                    height = screen_height + 800,
                    margin=go.layout.Margin(
                        l=50,
                        r=50,
                        b=1000,
                        t=100,
                        pad=4
        )      
                )
    fig = go.Figure(
        data = data,
        layout = layout
    )
    fig.update_xaxes(range=[comp_weeks.min(), comp_weeks.max()])


plotly.offline.plot(fig, filename=output_file, auto_open=False)