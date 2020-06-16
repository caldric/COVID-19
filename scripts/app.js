// URLs
const confirmedCurrent = 'https://covidtracking.com/api/v1/states/current.json';

// Data variables
const data = {};

// Functions
const getData = (apiURL) => $.ajax(apiURL);

const getCount = (arr, attr) => {
  let total = 0;
  arr.forEach(row => total += row[attr]);
  return total;
};

$(() => {
  getData(confirmedCurrent).then((jsonData) => {
    data.positive = jsonData;
    console.log(data.positive);
  });
});
