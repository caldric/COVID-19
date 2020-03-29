# Import required modules
import os

import imageio
import pandas as pd
import plotly.graph_objects as go

from os.path import join
from plotly.io import write_image


def main():
    infected_data = pd.read_excel(join('data', 'source.xlsx'), sheet_name='infected_state')
    colors = ['#ffffe5', '#fee391', '#fec44f', '#fe9929', '#ec7014', '#cc4c02', '#993404']
    bins = [0, 5, 50, 100, 500, 1000, 5000]
    normalized_bins = list(map(lambda n: n / bins[-1], bins))
    color_scale = [[normalized_bins[i], colors[i]] for i in range(len(colors))]

    infected_data['date'] = pd.to_datetime(infected_data['date'], format='%Y-%m-%d')
    infected_data = infected_data.loc[infected_data['date'] > '2020-02-29']
    dates = sorted(set(infected_data['date']))
    infected_data_at = {}
    for date in dates:
        infected_data_at[date] = infected_data.loc[infected_data['date'] == date].reset_index()

    if not os.path.exists('images'):
        os.mkdir('images')

    for i in range(len(dates)):
        data = infected_data_at[dates[i]]
        path = join('images', 'fig{}.png'.format(str(i).zfill(2)))
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
                       + '<br>Total cases: ' + '{:,}'.format(sum(data['infected_count'])),
            geo=dict(scope='usa')
        )
        write_image(fig, path, format='png')

    gif_writer('images')


def gif_writer(src, duration=None):
    paths = sorted([join(src, file) for file in os.listdir(src) if file != '.DS_Store'])
    gif = []
    for path in paths:
        gif.append(imageio.imread(path))

    if duration:
        imageio.mimsave('timeline.gif', gif, duration=duration)
    else:
        imageio.mimsave('timeline.gif', gif, duration=0.7)


if __name__ == '__main__':
    main()
