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

const getTotalConfirmed = (confirmedArr) => {
  let totalConfirmed = 0;
  for (let row of confirmedArr) {
    if (typeof row[latestDate] == 'string') {
      let confirmedCount = parseInt(row[latestDate]);
      totalConfirmed += confirmedCount;
    }
  }
  return totalConfirmed;
};

$(() => {
  getData(confirmedURL, 'confirmed');
  console.log(data.confirmed);
  console.log(getTotalConfirmed(data.confirmed));
});
