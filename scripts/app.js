// URLs
const currentURL = 'https://covidtracking.com/api/v1/states/current.json';

// Functions
const getData = (apiURL) => $.ajax(apiURL);

const getCount = (arr, attr) => {
  let total = 0;
  arr.forEach(row => total += row[attr]);
  return total;
};

const createSummary = (confirmedCount, deathsCount) => {
  const $summaryDiv = $('#summary');
  $summaryDiv.addClass('card');

  const $confirmedHeader = $('<h2>').text('Total Confirmed');
  const $confirmedCount = $('<p>').text(confirmedCount);
  const $deathsHeader = $('<h2>').text('Total Deaths');
  const $deathsCount = $('<p>').text(deathsCount);

  $summaryDiv.append($confirmedHeader, $confirmedCount, $deathsHeader, $deathsCount);
};

$(() => {
  getData(currentURL).then((jsonData) => {
    const currentConfirmed = getCount(jsonData, 'positive');
    const currentDeaths = getCount(jsonData, 'death');
    createSummary(currentConfirmed, currentDeaths);
  });
});
