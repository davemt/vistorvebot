function hangout(appData) {
    var hangoutUrl = gapi.hangout.getHangoutUrl();

    // Maybe the returned json from activate_session_url should contain the
    // websocket url

    console.log(hangoutUrl);
    jQuery.getJSON(appData.activate_session_url,
                   {hangout_url: hangoutUrl},
                   function(data) {
                       console.log(appData.websocket_control_url);
                       socket = new WebSocket(appData.websocket_control_url);
                       console.log("Opened socket");
                       jQuery('#hangoutSuccessDiv').text('hanging out: ');
                   });
}

function vistorveForward() {
  socket.send("forward");
}

function vistorveLeft() {
  socket.send("left");
}

function vistorveRight() {
  socket.send("right");
}

console.log("in hangout.js");
console.log(VBot.hangout.appData);
hangout(VBot.hangout.appData);
