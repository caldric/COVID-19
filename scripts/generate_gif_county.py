# Import required modules
import io
import os

import imageio
import pandas as pd
import plotly.figure_factory as ff
import requests

from os.path import join
from plotly.io import write_image


def main():
    # Establish color scale for choropleth map
    colors = ['#ffffe5', '#fee391', '#fec44f', '#fe9929', '#ec7014', '#cc4c02', '#993404', '#662506']
    bins = [5, 50, 100, 500, 1000, 5000]

    # Data variables
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/' \
          + 'csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
    infected_data = wrangle_data(url)
    dates = sorted(set(infected_data['date']))
    infected_data_at = {}
    for date in dates:
        infected_data_at[date] = infected_data.loc[infected_data['date'] == date].reset_index()

    # Create PNG files of the figure for each day and store in 'images/county_timeline' directory
    if not os.path.exists('images/county_timeline'):
        os.mkdir('images/county_timeline')

    for i in range(len(dates)):
        data = infected_data_at[dates[i]]
        path = join('images/county_timeline', '{}.png'.format(dates[i].strftime('%Y-%m-%d')))

        fig = ff.create_choropleth(
            fips=data['fips'],
            values=data['count'],
            binning_endpoints=bins,
            colorscale=colors,
            show_state_data=True,
            show_hover=True,
            centroid_marker={'opacity': 0},
            asp=2.9
        )
        fig.update_layout(
            title_text=dates[i].strftime('%B %d, %Y'),
            geo=dict(scope='usa')
        )
        write_image(fig, path, format='png')

    gif_writer('images/county_timeline')


def gif_writer(src, duration=None):
    """Combines images from src directory into one GIF"""
    paths = sorted([join(src, file) for file in os.listdir(src) if file != '.DS_Store'])
    gif = []
    for path in paths:
        gif.append(imageio.imread(path))

    if duration:
        imageio.mimsave('images/county_timeline.gif', gif, duration=duration)
    else:
        imageio.mimsave('images/county_timeline.gif', gif, duration=0.5)


def wrangle_data(url):
    content = requests.get(url).content
    raw_data = pd.read_csv(io.StringIO(content.decode('utf-8')))

    # Data wrangling
    # remove unneeded columns
    infected_data = raw_data.drop(
        columns=['UID', 'iso2', 'iso3', 'code3', 'Admin2', 'Province_State', 'Country_Region', 'Combined_Key']
    )
    # rename columns
    infected_data = infected_data.rename(columns={'FIPS': 'fips', 'Lat': 'lat', 'Long_': 'long'})
    # remove rows with null fips and coordinates
    infected_data = infected_data[(infected_data['fips'].notnull() & infected_data['lat'] != 0)]
    # standardize the fips
    infected_data['fips'] = infected_data['fips'].apply(lambda code: str(int(code)).zfill(5))
    # unpivot date columns
    infected_data = infected_data.melt(id_vars=['fips', 'lat', 'long'], var_name='date', value_name='count')
    # convert date strings to datetime objects
    infected_data['date'] = pd.to_datetime(infected_data['date'], format='%m/%d/%y')

    return infected_data


if __name__ == '__main__':
    main()
