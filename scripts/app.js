// URLs
const confirmedCurrent = 'https://covidtracking.com/api/v1/states/current.json';

// Data variables
const data = {};

// Functions
const getData = () => $.ajax({url: confirmedCurrent}).then((theData) => {
  console.log(theData);
  console.log(theData instanceof Array);
  console.log(getCount(theData));
});

const getCount = (arr) => {
  let total = 0;
  arr.forEach(row => total += row.positive);
  return total;
};

$(() => {
  getData();
});
