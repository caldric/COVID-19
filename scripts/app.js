// URLs
const confirmedCurrent = 'https://covidtracking.com/api/v1/states/current.json';

// Functions
const getData = (apiURL) => $.ajax(apiURL);

const getCount = (arr, attr) => {
  let total = 0;
  arr.forEach(row => total += row[attr]);
  return total;
};

$(() => {
  getData(confirmedCurrent).then((jsonData) => {
    const totalCurrentPositive = getCount(jsonData, 'positive');
    console.log(totalCurrentPositive);
  });
});
