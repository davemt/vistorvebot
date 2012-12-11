function hangout(appData) {
    var hangoutUrl = gapi.hangout.getHangoutUrl();

    // Maybe the returned json from activate_session_url should contain the
    // websocket url
    jQuery.getJSON(appData.activate_session_url,
                   {hangout_url: hangoutUrl},
                   function(data) {
                       socket = new WebSocket(appData.websocket_control_url);
                       jQuery('#hangoutSuccessDiv').text('hanging out: ');
                   });
}

function vistorveForward() {
  socket.send("VISTORVE.FORWARD");
}

function vistorveLeft() {
  socket.send("VISTORVE.LEFT");
}

function vistorveRight() {
  socket.send("VISTORVE.RIGHT");
}

function showParticipants() {
  var participants = gapi.hangout.getParticipants();

  var retVal = '<p>Participants: </p><ul>';

  for (var index in participants) {
    var participant = participants[index];

    if (!participant.person) {
      retVal += '<li>A participant not running this app</li>';
    }
    retVal += '<li>' + participant.person.displayName + '</li>';
  }

  retVal += '</ul>';

  var div = document.getElementById('participantsDiv');

  div.innerHTML = retVal;
}

