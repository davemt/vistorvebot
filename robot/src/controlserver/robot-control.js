// $(document).keydown()
// TODO: Do we want configurable velocity and turn radius?
// TODO: Add docking button
// TODO: Add event handling (crash into a wall etc)
// TODO: Add reset?

(function( $ ){
    var defaults = {
        errorHandler: function (errorText){console.log('ERROR:' + errorText);},
        messageHandler: function (messageText){console.log('MESSAGE:' + messageText);},
        controlServer: 'ws://localhost:9435/control',
        commandInterval: 500, // Length of time each command runs
        responseCodes: {error: 'ERROR', success: 'OK'},
        buttons: {
            forward: {selector: '.forward', keyCode: 38, mask: 0x1},
            backward: {selector: '.backward', keyCode: 40, mask: 0x8},
            left: {selector: '.left', keyCode: 37, mask: 0x4},
            right: {selector: '.right', keyCode: 39, mask: 0x2}
        }
    };

    var methods = {
        init : function( options ) {
            var that = this;
            return this.each(function(){
                var $this = $(this),
                    data = $this.data('robotControl'),
                    settings = $.extend(defaults, options);

                // If the plugin hasn't been initialized yet
                if ( ! data ) {
                    $this.data('robotControl', {
                        commandInterval : settings.commandInterval,
                        controlServer : settings.controlServer,
                        errorHandler: settings.onError,
                        messageHandler: settings.messageHandler,
                        buttons: settings.buttons,
                        responseCodes: settings.responseCodes,
                        currentCommand: 0x0
                    });
                    methods._createCommandMap.apply(that, [settings.buttons]);
                    methods.createListeners.apply(that, [settings.buttons]);
                    methods.createSocket.apply(that);
                }
            });
        },
        _createCommandMap : function () {
            return this.each(function(){
                var commands = {},
                $this = $(this),
                data = $this.data('robotControl'),
                buttons = data.buttons;
                // This maps our button combinations onto commands to send the socket
                commands[buttons.forward.mask] = 'forward';
                commands[buttons.backward.mask] = 'backward';
                commands[buttons.right.mask] = 'right';
                commands[buttons.left.mask] = 'left';
                commands[buttons.forward.mask | buttons.right.mask] = 'forward_right';
                commands[buttons.forward.mask | buttons.left.mask] = 'forward_left';
                commands[buttons.backward.mask | buttons.right.mask] = 'backward_right';
                commands[buttons.backward.mask | buttons.left.mask] = 'backward_left';

                data.commands = commands;
            });
        },
        createListeners : function (){
            var that = this;
            return this.each(function(){
                var $this = $(this),
                data = $this.data('robotControl');
                $(document).bind('keydown.robotControl', data, methods._keyEvent);
                $(document).bind('keyup.robotControl', data, methods._keyEvent);
                $.each(data.buttons, function (buttonName, buttonData){
                    var eventData = {buttonName: buttonName, globalData: data},
                    button = $this.find(buttonData.selector);
                    buttonData.button = button;
                    button.bind('mousedown.robotControl', eventData, methods._buttonEvent);
                    button.bind('mouseup.robotControl', eventData, methods._buttonEvent);
                });

                if (data.interval){
                    clearInterval(data.interval);
                };
                data.interval = setInterval(function (){
                    var command = data.commands[data.currentCommand];
                    if(command){
                        methods.sendMessage.apply(that, command);
                        console.log(command);
                    };
                }, data.commandInterval);
            });
        },
        _keyEvent : function (event){
            $.each(event.data.buttons, function (buttonName, buttonData){
                if (buttonData.keyCode == event.which){
                    event.data = {buttonName: buttonName, globalData: event.data};
                    methods._buttonEvent(event);
                }
            });
        },
        _buttonEvent : function (event){
            var buttonName = event.data.buttonName,
            mask = event.data.globalData.buttons[buttonName].mask;
            if (event.type.indexOf('down') != -1) { // Add the event
                event.data.globalData.buttons[buttonName].button.addClass('active');
                event.data.globalData.currentCommand = event.data.globalData.currentCommand | mask;
            }
            else { // Remove the event
                event.data.globalData.buttons[buttonName].button.removeClass('active');
                event.data.globalData.currentCommand = event.data.globalData.currentCommand & ~ mask;
            }
        },
        createSocket : function () {
            return this.each(function(){
                var $this = $(this),
                data = $this.data('robotControl');

                if ('WebSocket' in window) {
                    data.socket = new WebSocket(data.controlServer);
                } else if ('MozWebSocket' in window) {
                    data.socket = new MozWebSocket(data.controlServer);
                }
                data.socket.onmessage = function(event) {methods._handleSocketResponse(event, data.messageHandler, data.errorHandler, data.responseCodes);};
                data.socket.onopen = function () {data.messageHandler('Opened Socket');};
                data.socket.onerror = function () {data.messageHandler('Socket Error');};
                data.socket.onclose = function(event) {methods._handleSocketResponse(event, data.messageHandler);};
            });
        },
        sendMessage: function (message)  {
            return this.each(function(){
                var $this = $(this),
                data = $this.data('robotControl');
                if(!data.socket)
                    data.errorHandler('Tried to send a message, but not connectied');
                else
                    data.messageHandler('Sending Message: ' + message);
                    data.socket.send(message);
            });
        },
        _handleSocketResponse : function (event, messageHandler, errorHandler, responseCodes){
            var message = event.data;
            if (message.substring(0, responseCodes.error.length) == responseCodes.error)
                errorHandler(message);
            else
                messageHandler(message);
        },
        _handleSocketClose : function (event, messageHandler){
            // TODO: Might want to handle this in different way
            messageHandler('Closed Socket');
        },
        destroy : function( ) {
            return this.each(function(){

                var $this = $(this),
                    data = $this.data('robotControl');

                // Namespacing FTW
                $(document).unbind('.robotControl');
                data.socket.close();
                data.robotControl.remove();
                $this.removeData('robotControl');

            });
        }
    };

    $.fn.robotControl = function( method ) {
        if ( methods[method] ) {
            return methods[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.tooltip' );
        }
    };

})( jQuery );