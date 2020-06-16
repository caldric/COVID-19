// URLs
const timeSeriesURL = 'https://raw.githubusercontent.com/CSSEGISandData/'
  + 'COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/';
const confirmedURL = timeSeriesURL + 'time_series_covid19_confirmed_US.csv';
const deathsURL = timeSeriesURL + 'time_series_covid19_deaths_US.csv';

// Data variables
const latestDate = '6/15/20';
const data = {};

// Functions
const getData = (url, category) => Papa.parse(url, {
  download: true,
  header: true,
  complete: csv => {
    data[category] = csv.data;
  }
});

const getCount = (arr) => {
  let total = 0;
  for (let row of arr) {
    if (typeof row[latestDate] == 'string') {
      let confirmedCount = parseInt(row[latestDate]);
      total += confirmedCount;
    }
  }
  return total;
};

$(() => {
  getData(confirmedURL, 'confirmed');
  getData(deathsURL, 'deaths');

  console.log(data.confirmed);
  console.log(getCount(data.confirmed));
});
