# Import required modules
import io
import os

import imageio
import pandas as pd
import plotly.graph_objects as go
import requests

from os.path import join
from plotly.io import write_image


def main():
    # Establish color scale for choropleth map
    colors = ['#ffffe5', '#fee391', '#fec44f', '#fe9929', '#ec7014', '#993404']
    bins = [0, 1, 100, 1000, 5000, 10_000]
    normalized_bins = list(map(lambda n: n / bins[-1], bins))
    color_scale = [[normalized_bins[i], colors[i]] for i in range(len(colors))]

    # Data variables
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/' \
          + 'csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
    infected_data = wrangle_data(url)
    dates = sorted(set(infected_data['date']))
    infected_data_at = {}
    for date in dates:
        infected_data_at[date] = infected_data.loc[infected_data['date'] == date].reset_index()

    # Create PNG files of the figure for each day and store in 'images/state_timeline' directory
    if not os.path.exists('images/state_timeline'):
        os.mkdir('images/state_timeline')

    for i in range(len(dates)):
        data = infected_data_at[dates[i]]
        path = join('images/state_timeline', '{}.png'.format(dates[i].strftime('%Y-%m-%d')))
        total_cases = sum(data['infected_count'])
        if i > 0:
            new_cases = total_cases - sum(infected_data_at[dates[i - 1]]['infected_count'])
        else:
            new_cases = 0

        fig = go.Figure(data=go.Choropleth(
            locations=data['state_code'],
            z=data['infected_count'],
            locationmode='USA-states',
            zmin=0, zmax=bins[-1],
            colorscale=color_scale,
            autocolorscale=False,
            marker_line_color='black'
        ))
        fig.update_layout(
            title_text='<b>COVID-19 US Infected</b><br>Confirmed cases as of ' + dates[i].strftime('%B %d, %Y')
            + '<br>Total cases: ' + '{:,}<br>New cases: {:,}'.format(total_cases, new_cases),
            geo=dict(scope='usa')
        )
        write_image(fig, path, format='png')

    gif_writer('images/state_timeline')


def gif_writer(src, duration=None):
    """Combines images from src directory into one GIF"""
    paths = sorted([join(src, file) for file in os.listdir(src) if file != '.DS_Store'])
    gif = []
    for path in paths:
        gif.append(imageio.imread(path))

    if duration:
        imageio.mimsave('images/state_timeline.gif', gif, duration=duration)
    else:
        imageio.mimsave('images/state_timeline.gif', gif, duration=0.5)


def wrangle_data(url):
    # Lookup data
    us_state_codes = pd.read_csv(join('data', 'us_state_codes.csv'))
    us_state_coordinates = pd.read_csv(join('data', 'us_state_coordinates.csv'))
    us_state_lookups = pd.merge(us_state_codes, us_state_coordinates, on=['state'], how='inner')

    content = requests.get(url).content
    raw_data = pd.read_csv(io.StringIO(content.decode('utf-8')))

    # Data wrangling
    # remove unneeded columns
    infected_data = raw_data.drop(
        ['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Country_Region', 'Lat', 'Long_', 'Combined_Key'], axis=1
    )
    # rename state column
    infected_data = infected_data.rename({'Province_State': 'state'}, axis=1)
    # group by state
    infected_data = infected_data.groupby(['state']).sum().reset_index()
    # unpivot date columns
    infected_data = infected_data.melt(id_vars=['state'], var_name='date', value_name='infected_count')
    # transform date column from str to datetime
    infected_data['date'] = pd.to_datetime(infected_data['date'], format='%m/%d/%y')
    # merge state codes and coordinates to infected data
    infected_data = pd.merge(infected_data, us_state_lookups, on=['state'], how='right')
    # rearrange columns
    infected_data = infected_data[['state', 'state_code', 'latitude', 'longitude', 'date', 'infected_count']]

    return infected_data


if __name__ == '__main__':
    main()
