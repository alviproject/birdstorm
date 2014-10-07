var interval = undefined;

function make_connection(delay, channels) {
    if(interval!==undefined) {
        window.clearInterval(interval);
    }

    connection = new SockJS('/broadcast');

    connection.channels = channels;

    connection.is_connected = false;

    connection.subscribe = function (channel) {
        console.log("subscribing to ", channel);
        var message = {
            command: 'subscribe',
            channel: channel
        };
        message = JSON.stringify(message);
        connection.send(message);
    };

    connection.unsubscribe = function (channel) {
        console.log("unsubscribing ", channel);
        var message = {
            command: 'unsubscribe',
            channel: channel
        };
        message = JSON.stringify(message);
        connection.send(message);
    };

    connection.onopen = function () {
        console.log("opening broadcast connection");
        this.is_connected = true;

        console.log("connecting to requested broadcast channels");
        for (var channel in this.channels) {
            this.subscribe(channel);
        }
    };

    connection.onmessage = function (e) {
        console.log('receiving message', e.data);
        var channel = e.data['channel'];
        //var channel_class = channel.split('.')[0];
        this.channels[channel](e.data);
    };

    connection.onclose = function () {
        console.log("broadcast connection closed, trying to reconnect in ", delay);
        this.is_connected = false;
        var connection_channels = this.channels;
        interval = window.setInterval(function () {
            var new_delay = 2*(delay+1);
            if(new_delay > 1000){
                new_delay = 1000
            }
            make_connection(new_delay, connection_channels)
        }, delay);
    };

    connection.create_subscription = function(channel_class, callback) {
        var subscription = {};

        subscription.subscribe = function(channel_instance) {
            if(!channel_instance) {
                return;
            }
            //unsubscribe from previous channel instance
            if(this.channel !== undefined) {
                connection.unsubscribe(this.channel);
                delete connection.channels[this.channel];
            }

            //subscribe to a new instance
            this.channel = channel_class + '.' + channel_instance;
            connection.channels[this.channel] = callback;
            if (connection.is_connected) {
                connection.subscribe(this.channel);
            }
        };
        return subscription;
    };

    return connection;
}

var connection = make_connection(0, {});
