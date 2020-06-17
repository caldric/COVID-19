// Data
const states = [
  {name: 'Alabama', code: 'AL'},
  {name: 'Alaska', code: 'AK'},
  {name: 'Arizona', code: 'AZ'},
  {name: 'Arkansas', code: 'AR'},
  {name: 'California', code: 'CA'},
  {name: 'Colorado', code: 'CO'},
  {name: 'Connecticut', code: 'CT'},
  {name: 'Delaware', code: 'DE'},
  {name: 'District of Columbia', code: 'DC'},
  {name: 'Florida', code: 'FL'},
  {name: 'Georgia', code: 'GA'},
  {name: 'Hawaii', code: 'HI'},
  {name: 'Idaho', code: 'ID'},
  {name: 'Illinois', code: 'IL'},
  {name: 'Indiana', code: 'IN'},
  {name: 'Iowa', code: 'IA'},
  {name: 'Kansas', code: 'KS'},
  {name: 'Kentucky', code: 'KY'},
  {name: 'Louisiana', code: 'LA'},
  {name: 'Maine', code: 'ME'},
  {name: 'Maryland', code: 'MD'},
  {name: 'Massachusetts', code: 'MA'},
  {name: 'Michigan', code: 'MI'},
  {name: 'Minnesota', code: 'MN'},
  {name: 'Mississippi', code: 'MS'},
  {name: 'Missouri', code: 'MO'},
  {name: 'Montana', code: 'MT'},
  {name: 'Nebraska', code: 'NE'},
  {name: 'Nevada', code: 'NV'},
  {name: 'New Hampshire', code: 'NH'},
  {name: 'New Jersey', code: 'NJ'},
  {name: 'New Mexico', code: 'NM'},
  {name: 'New York', code: 'NY'},
  {name: 'North Carolina', code: 'NC'},
  {name: 'North Dakota', code: 'ND'},
  {name: 'Ohio', code: 'OH'},
  {name: 'Oklahoma', code: 'OK'},
  {name: 'Oregon', code: 'OR'},
  {name: 'Pennsylvania', code: 'PA'},
  {name: 'Rhode Island', code: 'RI'},
  {name: 'South Carolina', code: 'SC'},
  {name: 'South Dakota', code: 'SD'},
  {name: 'Tennessee', code: 'TN'},
  {name: 'Texas', code: 'TX'},
  {name: 'Utah', code: 'UT'},
  {name: 'Vermont', code: 'VT'},
  {name: 'Virginia', code: 'VA'},
  {name: 'Washington', code: 'WA'},
  {name: 'West Virginia', code: 'WV'},
  {name: 'Wisconsin', code: 'WI'},
  {name: 'Wyoming', code: 'WY'}
];


// URLs
const currentURL = 'https://covidtracking.com/api/v1/states/current.json';


// General functions
const getData = (apiURL) => $.ajax(apiURL);

const getTotalCount = (arr, attr) => {
  let total = 0;
  arr.forEach(row => total += row[attr]);
  return total;
};

const extractRelevantData = (jsonData, states, targetKeys) => {
  states.forEach(state => {
    const jsonState = jsonData.filter(row => row.state == state.code);
    if (jsonState.length == 1) {
      targetKeys.forEach(field => state[field] = jsonState[0][field]);
    } else {
      targetKeys.forEach(field => state[field] = null);
    }
  });
};

String.prototype.toTitleCase = function() {
  return this[0].toUpperCase() + this.slice(1);
};

const addCommaSeparator = (num) => {
  // Orignal source: https://bit.ly/3fvdMWD
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};


// DOM functions
const createSummary = (confirmedCount, deathsCount) => {
  // Locate target
  const $targetDiv = $('#summary');
  $targetDiv.addClass('card');

  // Generate content
  const $confirmedHeader = $('<h2>').text('Total Confirmed');
  const $confirmedCount = $('<p>').text(confirmedCount);
  const $deathsHeader = $('<h2>').text('Total Deaths');
  const $deathsCount = $('<p>').text(deathsCount);

  // Add content to DOM
  $targetDiv.append($confirmedHeader, $confirmedCount, $deathsHeader, $deathsCount);
};

const createAttrByState = (states, $target, targetKey, description) => {
  // Locate target
  const $targetDiv = $target;
  $targetDiv.addClass('card');

  // Generate header content
  const $header = $('<h2>').text(`${description.toTitleCase()} by State`);
  $targetDiv.append($header);

  // Generate data by state in descending order
  sortedStates = JSON.parse(JSON.stringify(states));
  sortedStates = states.sort((a, b) => b.positive - a.positive);
  sortedStates.forEach(state => {
    const $newItem = $('<p>').text(`${state.name}: ${state[targetKey]}`);
    $targetDiv.append($newItem);
  });
};

const createImgCard = ($target, headerText, imgSrc='', imgAlt='') => {
  // Locate target
  const $targetDiv = $target;
  $targetDiv.addClass('card');

  const $header = $('<h2>').text(headerText);
  const $img = $('<img>').attr('src', imgSrc);
  $img.attr('alt', imgAlt);

  $targetDiv.append($header, $img);
};


$(() => {
  getData(currentURL).then((jsonData) => {
    // Extract relevant data
    const relevantFields = ['positive', 'death'];
    extractRelevantData(jsonData, states, relevantFields);

    // Card 1: Summary Data
    const currentConfirmed = getTotalCount(jsonData, 'positive');
    const currentDeaths = getTotalCount(jsonData, 'death');
    createSummary(currentConfirmed, currentDeaths);

    // Card 2: Confirmed by State
    createAttrByState(states, $('#confirmed-by-state'), 'positive', 'confirmed');

    // Card 3: Deaths by State
    createAttrByState(states, $('#deaths-by-state'), 'death', 'deaths');

    // Card: Choropleth Map
    createImgCard(
      $('#choropleth-map'), 'Choropleth Map', './images/state_timeline.gif',
      'US choropleth map of confirmed COVID-19 cases'
    );

    // Card: SIR Model
    createImgCard(
      $('#model'), 'SIR Model', './images/projection.png',
      'SIR model for COVID-19'
    );

    // Card: SIR model fit
    createImgCard(
      $('#model-fit'), 'SIR Model Fit', './images/fit.png',
      'SIR model fit for COVID-19'
    );
  });
});
