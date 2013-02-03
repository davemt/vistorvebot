function hangout() {
    var hangoutUrl = gapi.hangout.getHangoutUrl();

    jQuery.getJSON(VBot.appData.activate_session_url,
                   {hangout_url: hangoutUrl},
                   function(data) {
                       /* XXX FIXME:
                        * In firefox the following fails with:
                        * SecurityError The operation is insecure
                        */
                       VBot.socket = new WebSocket(VBot.appData.websocket_control_url);
                   });
}

function vistorveForward() {
  VBot.socket.send("forward");
}

function vistorveLeft() {
  VBot.socket.send("left");
}

function vistorveRight() {
  VBot.socket.send("right");
}

hangout();
