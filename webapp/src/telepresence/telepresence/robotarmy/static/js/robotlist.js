(function ($) {
     $(document).ready(
         function () {
             $('#robot_list input[type="button"]').click(
                 function (){
                     var robotId = $(this).data('robot-id'),
                     hangoutURL = $(this).data('hangout-url');
                     $.getJSON('/robotarmy/robot-initialize-session/'+robotId+'/',
                               function (data){
                                   if (data.error){
                                       $('#robot-errors').text('ERROR: ' + data.message);
                                   }
                                   else {
                                       window.open(hangoutURL + '&gd=' +
                                                   encodeURI(data));
                                   }
                     });
                 });
     });
} (jQuery));
