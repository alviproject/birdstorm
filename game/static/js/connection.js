var connection = new SockJS('/broadcast');

connection.channels = {};
connection.is_connected = false;

connection.send_connect = function (channel) {
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
    console.log(this.channels);
    var channel = e.data['channel'];
    //var channel_class = channel.split('.')[0];
    this.channels[channel](e.data);
};

connection.onclose = function () {
    console.log("closing broadcast connection");
};

connection.add_channel = function(channel, callback) {
    this.channels[channel] = callback;
    if(this.is_connected) {
        this.send_connect(channel);
    }
};

//end of SockJS connection
