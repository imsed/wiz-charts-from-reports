import dash
from dash import html
from dash import dcc
import pandas as pd
import plotly.graph_objs as go
import random

#initialize the issue report
issue_report = '<put the path of the issue report>'

# read the data from a CSV file
origin_df = pd.read_csv(issue_report)

# mapping of some specific values to color for the pie chart
wiz_colors = {'OPEN': 'red', 'RESOLVED': 'green','IN_PROGRESS':'orange','INFORMATIONAL':'lightgrey','REJECTED':'darkgrey','LOW': 'lightblue', 'MEDIUM': 'darkorange', 'HIGH': 'red', 'CRITICAL': 'darkred'}

# set the default selected project
selected_project = 'All Projects'

# list of use cases for pie charts. These are based on the column names. If you need a new use case for pie charts just add it to the list
pie_chart_filters = ['Status','Severity','Project Names','Resource Platform', 'Subscription ID', 'Resource Region', 'Resource Type']

# list of use cases for line charts. These are based on the column names. If you need a new use case for line charts just add it to the list
line_chart_filters = ['Project Names','Severity','Resource Platform','Subscription ID']

# convert  datacolumns to datetime format 
origin_df['Created At'] = pd.to_datetime(origin_df['Created At'])
origin_df['Resolved Time'] = pd.to_datetime(origin_df['Resolved Time'])

# fill empty values with defaults
origin_df['Subscription ID'].fillna(value='No Subscription', inplace=True)
origin_df['Project Names'].fillna(value='No Project', inplace=True)
origin_df['Resource Platform'].fillna(value='Unknown', inplace=True)
origin_df['Resource Type'].fillna(value='Unknown', inplace=True)
origin_df['Resource Region'].fillna(value='Unknown', inplace=True)

# set the data to be used
df = origin_df

# helper function to extract unique project names from a DataFrame. Main challenge is Project Names column can contain multiple projects
def get_wiz_projects(df)-> list:
    """
    helper to retrieve the list of Wiz Project from the Project Names column
    We need it because multiple Wiz projects can share the same OU/Subscription

    Parameters:
        - data frame

    Returns:
        - List of unique Wiz Projects
    """
    non_sorted_projects = df['Project Names'].unique()
    projects = set()
    for p in non_sorted_projects:
        projects.update(p.split(', '))
    return list(projects)

# list of available projects. 
WIZ_PROJECTS = ['All Projects'] + get_wiz_projects(df)

# list of available resource platforms
RESOURCE_PLATFORMS =  ['All Resource Platforms'] + list(df['Resource Platform'].unique())

# list of available subscription IDs
SUBSCRIPTON_IDS =  ['All Subscriptions'] + list(df['Subscription ID'].unique())

# list of available Severities

SEVERITIES = ['All Severities','CRITICAL','HIGH','MEDIUM','LOW','INFORMATIONAL']



def pie_chart_use_cases(df, selected_project)->list:
    """
    Creates a list of Pie charts Based on pie_chart_filters

    Parameters:
        - data frame and Wiz Projects

    Returns:
        - List pie charts
    """

    pie_charts = []
    # Retrieve dynamicaly the list of Status.
    status_values = df['Status'].unique()
    
    # Data and layout for the open and resolved issues pie chart
    open_resolved_issues_pie_chart_data = [
        {
            'labels': status_values,
            'values': [df['Status'].value_counts()[status] for status in status_values],
            'type': 'pie',
            'hole': 0.6,
            'textposition': 'inside',
            'marker': {'colors': [wiz_colors.get(label,f'#{random.randint(0, 0xffffff):06x}') for label in status_values]}
        }
    ]
    open_resolved_issues_pie_chart_layout = {
        'title': f'All Issues by Status',
        'visible': True,
        'margin': {'t': 50, 'b': 50, 'l': 0, 'r': 0}
    }
    
    # Create graph object for open and resolved issues pie chart
    graph = {
        'id': 'open-resolved-issues-by-Status-pie-chart',
        'data': open_resolved_issues_pie_chart_data,
        'layout': open_resolved_issues_pie_chart_layout
    }
    pie_charts.append(graph)
    
    if selected_project == 'All Projects':
        wiz_projects = WIZ_PROJECTS
    else:
        wiz_projects = [selected_project] 
    # Loop over filter use cases and compute the necessary counts
    for filter in pie_chart_filters:
        if filter == 'Project Names':
            # Compute counts for issues by project name
            for status in status_values:
                labels = []
                values = []
                for project_name in wiz_projects:
                    labels.append(project_name)
                    values.append(df[df['Status'] == status][filter].str.contains(project_name).sum())
                status_issues_byfilter_pie_chart_data = [
                    {
                        'labels': labels,
                        'values': values,
                        'type': 'pie',
                        'hole': 0.6,
                        'textposition': 'inside',
                        'marker': {'colors': [wiz_colors.get(label,f'#{random.randint(0, 0xffffff):06x}') for label in labels]}
                    }
                ]
                status_issues_byfilter_pie_chart_layout = {
                    'title': f'{status} Issues by {filter}',
                    'visible': True,
                    'margin': {'t': 50, 'b': 50, 'l': 0, 'r': 0}
                }
                
                # Create graph object for issues by project name pie chart
                graph = {
                    'id': f'{status}-issues-by-{filter}-pie-chart',
                    'data': status_issues_byfilter_pie_chart_data,
                    'layout': status_issues_byfilter_pie_chart_layout
                }
                pie_charts.append(graph)
        elif filter != 'Status':
            # Compute counts for issues by filter option (severity, platform, etc.)
            for status in status_values:
                # Select rows with the specific status and group by the filter option
                status_issues_groupby_filter = df[df['Status'] == status][filter].value_counts().reset_index(name='Count')
                # Shorten labels to 36 characters for better display
                labels = [label[:36] for label in status_issues_groupby_filter['index']]
                values = status_issues_groupby_filter['Count']
                # Define the data and layout of the pie chart
                status_issues_byfilter_pie_chart_data = [
                    {'labels': labels, 'values': values, 'type': 'pie',
                    'hole': 0.6, 'textposition': 'inside', 'width': 100, 'height': 100,
                    'marker': {'colors': [wiz_colors.get(label, f'#{random.randint(0, 0xffffff):06x}')
                                            for label in labels]}
                    },
                ]
                status_issues_byfilter_pie_chart_layout = {
                    'title': f'{status}  Issues by {filter}', 'visible': True,
                    'margin': {'t': 50, 'b': 50, 'l': 0, 'r': 0}
                }            
                # Create the graph object with an ID and add it to the list of pie charts
                graph = {'id': f'{status}-issues-by-{filter}-pie-chart',
                        'data': status_issues_byfilter_pie_chart_data,
                        'layout': status_issues_byfilter_pie_chart_layout}
                pie_charts.append(graph)

    # Return the list of pie charts
    return pie_charts

def cumulative_line_chart_df(df):
    created_issues_daily_count = df.set_index('Created At').resample('D').size().fillna(0).reset_index(name='Count_created')
    resolved_issues_daily_count = df[df['Status'].isin(['RESOLVED', 'REJECTED'])].set_index('Resolved Time').resample('D').size().fillna(0).reset_index(name='Count_resolved')   
    # Merge created and resolved counts into a single DataFrame based on date using an outer join
    if not created_issues_daily_count.empty and not resolved_issues_daily_count.empty:
        open_issues_count = pd.merge(created_issues_daily_count, resolved_issues_daily_count, left_on='Created At', right_on='Resolved Time', how='outer', suffixes=('_created', '_resolved'))
    else:
        if created_issues_daily_count.empty and resolved_issues_daily_count.empty:
            open_issues_count = pd.DataFrame(columns=['Created At', 'Resolved Time', 'Count_created', 'Count_resolved'])
        elif created_issues_daily_count.empty:
            open_issues_count = resolved_issues_daily_count.copy()
            open_issues_count['Created At'] = open_issues_count['Resolved Time']
            open_issues_count['Count_created'] = 0
        else:
            open_issues_count = created_issues_daily_count.copy()
            open_issues_count['Resolved Time'] = open_issues_count['Created At']
            open_issues_count['Count_resolved'] = 0

    # Fill any missing values in the 'Count_created' and 'Count_resolved' columns with 0
    open_issues_count['Count_created'] = open_issues_count['Count_created'].fillna(0)
    open_issues_count['Count_resolved'] = open_issues_count['Count_resolved'].fillna(0)

    # Use either 'Created At' or 'Resolved Time' as the 'Date' column and fill any missing values
    open_issues_count['Date'] = open_issues_count['Created At'].fillna(open_issues_count['Resolved Time'])

    # Calculate the cumulative sum of open issues
    open_issues_count['Cumulative Open'] = open_issues_count['Count_created'] - open_issues_count['Count_resolved']
    open_issues_count['Cumulative Open'] = open_issues_count['Cumulative Open'].cumsum()
    return open_issues_count

def line_chart_use_cases (df,selected_project)->list:
    """
    Creates a list of Line charts Based on line_chart_filters

    Parameters:
        - data frame

    Returns:
        - List of line charts
    """
    # Initialize an empty list to store the line chart data and layout for each filter option
    line_charts =[]

    # Loop over all filter options
    for filter in line_chart_filters:
        # Initialize an empty list to store the line chart data for the current filter option
        line_charts_data =[]

        # Calculate daily counts for All created and ALL resolved issues
        open_issues_count = cumulative_line_chart_df(df)
        line_charts_data+=[{'x': open_issues_count['Date'], 'y': open_issues_count['Cumulative Open'], 'type': 'line', 'name': 'ALL'}]

        # Calculate daily counts for created and resolved issues by project (special filter, uses contains instead of equal)
        if filter == "Project Names":
                if selected_project == 'All Projects':
                    wiz_projects = [p for p in WIZ_PROJECTS if p !=  'All Projects']
                else:
                    wiz_projects = [selected_project]
                for project_name in wiz_projects:
                    df_filter= df [df[filter].str.contains(project_name)]
                    open_issues_count = cumulative_line_chart_df(df_filter)
                    line_charts_data+=[{'x': open_issues_count['Date'], 'y': open_issues_count['Cumulative Open'], 'type': 'line', 'name': f'{project_name[:36]}'}]

        else:    
        # Calculate daily counts for created and resolved issues by filter
            for f in df[filter].unique():
                df_filter = df[df[filter]==f]
                open_issues_count = cumulative_line_chart_df(df_filter)
                line_charts_data+=[{'x': open_issues_count['Date'], 'y': open_issues_count['Cumulative Open'], 'type': 'line', 'name': f'{f[:36]}'}]

        # Combine all line chart data for the current filter option
        filter_line_chart_data = (line_charts_data)

        # Define the layout for the current line chart
        filter_line_chart_layout = {
            'title': f'Issues over Time by {filter}',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Number of Issues'}
        }

        # Combine the line chart data and layout into a dictionary and append it to the list of line charts
        graph={
        'id':f'issues-{filter}-line-chart',
        'data': filter_line_chart_data,
        'layout': filter_line_chart_layout
        }
        line_charts.append(graph)

    # Return the list of line charts
    return line_charts

def create_figure_chart(data,layout)->dict:
    """
    create a plotly figure from data and layout dictionaries

    Parameters:
        - data and layout

    Returns:
        - Figure dictionary
    """
    return {
        'data': data,
        'layout': layout
    }

def generate_pie_chart_div(pie_charts)->list:
    """
     generate a list of divs containing pie charts grouped by filter

    Parameters:
        - pie charts

    Returns:
        - list of divs
    """
    pie_chart_groups = {filter: [] for filter in pie_chart_filters}  # create empty list for each filter group

    # group pie charts by filter
    for chart in pie_charts:
        filter_name = chart['id'].split('-')[-3] # extract filter name from chart id
        pie_chart_groups[filter_name].append(chart)

    # create a div for each filter group
    pie_chart_divs = {}
    for filter, charts in pie_chart_groups.items():
        # create a list of pie charts for each filter
        chart_divs = [dcc.Graph(id=chart['id'], figure=create_figure_chart(chart['data'], chart['layout']),style={'width': '25%','max-height':'1000px'}) for chart in charts]
        # create a div for the group and add the chart divs
        pie_chart_div = html.Div([
            html.H2(f'Issues by {filter}'),
            html.Div(children=chart_divs,style={'display': 'flex','flex-wrap': 'wrap'})
        ],id=f'id-div-{filter.strip()}')
        pie_chart_divs[filter]=pie_chart_div

    return pie_chart_divs

# Generate pie charts 
pie_charts = pie_chart_use_cases(df, 'All Projects')
# Group pie charts of the same pie chart fileter on the same Divs 
pie_charts_div = html.Div(children=list(generate_pie_chart_div(pie_charts).values()))

# Generate line charts
line_charts = line_chart_use_cases(df,'All Projects')
line_charts_html = [
    dcc.Graph(id=chart['id'], figure=create_figure_chart(chart['data'], chart['layout']), style={'width': '100%'})
    for chart in line_charts
]
# Combine the line charts into a single div
line_charts_div = html.Div(children=line_charts_html,style={'display': 'flex', 'flex-wrap': 'wrap'})

# Start a Dash app
app = dash.Dash()

# Define the layout of the web page using Dash HTML components, These are the parameters when the page first start. update_chart function is used when the page is refreshed.
app.layout = html.Div(children=[
    # Add dropdowns to select project name, resource platform, and subscription ID
    html.Div([
        html.Label('Project Name'),
        dcc.Dropdown(
            id='project-dropdown',
            options=[{'label': i, 'value': i} for i in  WIZ_PROJECTS],
            value='All Projects',
            style={'width': '300px'}
        ),
        html.Label('Severity'),
        dcc.Dropdown(
            id='severity-dropdown',
            options=[{'label': i, 'value': i} for i in  SEVERITIES],
            value='All Severities',
            style={'width': '300px'}
        ),
        html.Label('Resource Platform'),
        dcc.Dropdown(
            id='csp-dropdown',
            options=[{'label': i, 'value': i} for i in   RESOURCE_PLATFORMS],
            value='All Resource Platforms',
            style={'width': '300px'}
        ),
        html.Label('Subscription ID'),
        dcc.Dropdown(
            id='subscription-dropdown',
            options=[{'label': i, 'value': i} for i in   SUBSCRIPTON_IDS],
            value='All Subscriptions',
            style={'width': '400px'}
        )
    ],style={'display': 'flex','flex-wrap': 'wrap'}),
    
    # Add a header for the line charts section
    html.H1(children='Wiz Issues over Time'), 
    # Insert the line charts section
    line_charts_div,
    
    # Add a header for the pie charts section
    html.H1(children='Wiz Issues Pie Charts'),   
    # Insert the pie charts section
    pie_charts_div,
])

# Define the output elements for the callback function 
output_id_div_filters = [dash.dependencies.Output(f'id-div-{filter.strip()}', 'children') for filter in pie_chart_filters]
output_line_charts = [dash.dependencies.Output(chart['id'], 'figure') for chart in line_charts]

# Define the callback function to update the charts based on user inputs 
@app.callback(
    output_line_charts, output_id_div_filters,
    [dash.dependencies.Input('project-dropdown', 'value'),dash.dependencies.Input('severity-dropdown', 'value'),dash.dependencies.Input('csp-dropdown', 'value'),dash.dependencies.Input('subscription-dropdown', 'value')]
)
def update_chart(selected_project, selected_severity,selected_csp, selected_subscription)->list:
    """
    This function is called when the user selects an option in any of the dropdown menus. 
    It updates the charts displayed on the web page based on the selected inputs. 
    """
    df = origin_df
    
    # Filter the data based on the selected project
    if selected_project != 'All Projects':
        df = df[df['Project Names'].str.contains(selected_project)]

    # Filter the data based on the severity

    if selected_severity != 'All Severities':
        df = df[df['Severity'] == selected_severity]

    # Filter the data based on the selected resource platform
    if selected_csp != 'All Resource Platforms':
        df = df[df['Resource Platform'] == selected_csp]
    
    # Filter the data based on the selected subscription ID
    if selected_subscription != 'All Subscriptions':
        df = df[df['Subscription ID'] == selected_subscription]


    
    # Refresh the pie charts based on the filtered data
    refresh_pie_charts = pie_chart_use_cases(df, selected_project)
    pie_chart_divs = generate_pie_chart_div(refresh_pie_charts)

    div_children = []

    for filter_name in pie_chart_filters:
        if filter_name in pie_chart_divs:
            div_children.append(pie_chart_divs[filter_name])

    # Refresh the line charts based on the filtered data
    refresh_line_charts = line_chart_use_cases(df,selected_project)
    updated_line_charts_figure = [create_figure_chart(chart['data'], chart['layout']) for chart in refresh_line_charts]

    # Return the updated line charts and pie charts as a list of figures and divs
    return updated_line_charts_figure + div_children

@app.callback(
    [dash.dependencies.Output('subscription-dropdown', 'value'),
     dash.dependencies.Output('subscription-dropdown', 'options'),
     dash.dependencies.Output('severity-dropdown', 'value'),
     dash.dependencies.Output('severity-dropdown', 'options')],
    [dash.dependencies.Input('project-dropdown', 'value'),
     dash.dependencies.Input('csp-dropdown', 'value')]
)
def update_dropdowns(selected_project, selected_csp):
    """
    This function is called when the user selects an option in any of the dropdown menus. 
    It updates the Subscription ID drop down menu 
    """
    # Filter the dataframe based on the selected project and resource platform
    if selected_project == 'All Projects':
        df = origin_df
    else:
        df = origin_df[origin_df['Project Names'].str.contains(selected_project)]
    
    if selected_csp != 'All Resource Platforms':
        df = df[df['Resource Platform'] == selected_csp]
    
    # Get the list of unique resource platforms and subscription IDs
    subscription_ids = df['Subscription ID'].unique()

    severities = df ['Severity'].unique()
    
    # Create a list of dictionaries for the options in the dropdown boxes
    subscription_options = [{'label': 'All Subscriptions', 'value': 'All Subscriptions'}] + [{'label': subscription, 'value': subscription} for subscription in subscription_ids]
    
    severity_options = [{'label': 'All Severities', 'value': 'All Severities'}] + [{'label': severity, 'value': severity} for severity in severities]

    
    # Return the default value and the updated list of options for the subscription dropdown
    return 'All Subscriptions', subscription_options, 'All Severities',severity_options


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

