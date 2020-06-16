// URLs
const confirmedCurrent = 'https://covidtracking.com/api/v1/states/current.json';

// Data variables
const data = {};

// Functions
const getData = () => $.ajax({url: confirmedCurrent}).then((theData) => {
  console.log(theData);
  console.log(theData instanceof Array);
  console.log(getCount(theData, 'positive'));
});

const getCount = (arr, attr) => {
  let total = 0;
  arr.forEach(row => total += row[attr]);
  return total;
};

$(() => {
  getData();
});
