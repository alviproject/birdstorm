var interval = undefined;

function make_connection(delay, channels) {
    if(interval!==undefined) {
        window.clearInterval(interval);
    }

    connection = new SockJS('/broadcast');

    connection.channels = channels;

    connection.is_connected = false;

    connection.send_connect = function (channel) {
        console.log("connecting to ", channel);
        var message = {
            command: 'connect',
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
            this.send_connect(channel);
        }
    };

    connection.onmessage = function (e) {
        console.log('reveiving message', e.data);
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

    connection.add_channel = function (channel, callback) {
        this.channels[channel] = callback;
        if (this.is_connected) {
            this.send_connect(channel);
        }
    };
    return connection;
}

var connection = make_connection(0, {});
