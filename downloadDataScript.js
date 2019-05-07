/*
	Usage:

	1. Navigate: to http://climate.weather.gc.ca/prods_servs/cdn_climate_summary_e.html
	2. Change the Year selector to any year before 2019, for example, 2015.
	3. Make sure the 'Data Format' check box is selecting 'CSV'
	3. Copy and paste the 'sleep' function below on the console and then hit enter
	4. Copy and paste the 'downloadData' function below on the console and then hit enter
	5. Run downloadData() on the console.
	6. Wait until all the files have been downloaded, it should download 108 files.

*/

var sleep = (ms) => {
  return new Promise(resolve => setTimeout(resolve, ms));
}

var downloadData = async () => {
	let buttons = Array.from(document.getElementsByTagName('input')).filter(v => v.value == "Download data");
	if(buttons.length === 0) {
		alert('Download button not found!');
		return;
	} 
	let button = buttons[0];
	let yearSelector = document.getElementById('intYear');
	let monthSelector = document.getElementById('intMonth');
	let yearSelectorBase = 1840;
	let initialYear = 2009;
	let endYear = 2017;
	let provinceSelector = document.getElementById('prov');
	provinceSelector.selectedIndex = 2; // Select British Columbia

	for(let year = initialYear ; year <= endYear ; ++year) {
		yearSelector.selectedIndex = year - yearSelectorBase;
		for(let i = 0 ; i < 12 /* number of months */ ; ++i) {
			monthSelector.selectedIndex = i;
			button.click();
  			await sleep(3000);
		};
	}
}
