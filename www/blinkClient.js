// Global constants

// rate in Hz
CLOCKSPEED = 5;

// colors
TESTPATTERN = {
    0: "rgb(0, 0, 0)"
  , 1: "rgb(255, 0, 0)"
  , 2: "rgb(255, 255, 0)"    
  , 3: "rgb(0, 255, 0)"
  , 4: "rgb(0, 255, 255)"
  , 5: "rgb(0, 0, 255)"
  , 6: "rgb(255, 0, 255)"
  , 7: "rgb(255, 255, 255)"
}
// Functions for encoding

// Takes ASCII string, returns binary [ "1", "0" ] array
function a2b(ourString) {
  var array = ourString.split('').map(function(character) {
      
    binSet = character.charCodeAt(0).toString(2);
    itter = (8-binSet.length);
      
    for (i=0;i<itter;i++){
	    binSet="0"+binSet;
    }
      return binSet;
});
    return array.join('').split('');
}

// This function takes an array from a2b and blinks the div
function blinkDiv(data, style) {
  var clock = 1000/CLOCKSPEED;
  var i = 1;
  var testVal=0
  
  var blinkDiv = $('#blink-div');

  // Disable all children of the form element
  $('form > *').attr('disabled', true);

  var dataState = dataState || null;
  var loops = data.length * 2;
    
  console.log(data);

  // Interval (timer loop)
  var clockInterval = setInterval(function() {

    var clockState = i % 2; 

    // Sample data everytime clock is 1
    if( clockState === 1 ){
      dataState = data.shift();
    }

    var xord = clockState ^ dataState;

    console.log('clk', clockState);
    console.log('data', dataState);
    console.log('xor', xord);
    
    if (style==1){
        redValue=(xord*255);
        greenValue=0
        blueValue=0
        divColor="rgb("+redValue+", "+greenValue+", "+blueValue+")";
    }
    if (style==2){
        redValue=(dataState*255);
        greenValue=0
        blueValue=(clockState*255);
        divColor="rgb("+redValue+", "+greenValue+", "+blueValue+")";
    }      
    if (style==3){
        divColor=TESTPATTERN[testVal];
        testVal++;
    }    
      
    blinkDiv.css('background-color', divColor);

    if( i === loops ) {
      console.log('looped over:', i);  
      clearInterval(clockInterval);
      $('form > *').attr('disabled', false);
    }

    i++;

  }, clock);
}

// Event listeners
$('#encode-form').submit( function(e) {

  // Prevent the browser from attempting to actually submit
  e.preventDefault();
  var ourTextBox = $('#our-string');

  if (ourTextBox.val().length > 0)
  {
      // Get our string and then encode from the textbox
      var binaryArray = a2b( ourTextBox.val() );
    
      // Blink our div
      blinkDiv(binaryArray,2);
  }
    
    
// Clear text box
ourTextBox.val('');
    
});