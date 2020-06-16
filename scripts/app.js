const confirmedURL = 'https://raw.githubusercontent.com/CSSEGISandData/'
  + 'COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'
  + 'time_series_covid19_confirmed_US.csv';

let confirmedData;

console.log(confirmedURL);

Papa.parse(confirmedURL, {
  download: true,
  header: true,
  complete: csv => {
    confirmedData = csv.data;
    console.log(csv.data);
    const objKeys = Object.keys(csv.data[0]);
    console.log(objKeys[objKeys.length - 1]);

    // console.log(csv.data[0]['6/15/20']);
    let totalInfected = 0;
    for (let row of csv.data) {
      if (typeof row['6/15/20'] == 'string') {
        totalInfected += parseInt(row['6/15/20']);
      }
    }
    console.log(totalInfected);
  }
});

$(() => {
});
