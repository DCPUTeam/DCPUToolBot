// check if the config is there
if (!require('fs').existsSync('./config.js')){
	console.log("First create config.js! Copy config_example.js as a template!");
	process.exit(1);
}

var net = require('net'),
    config = require('./config'),
    request = require('request');

var client = net.connect({host: config.host, port: config.port},
    function() {
        console.log('client connected');
        client.write('PASS ' + config.pass + '\r\n');
        client.write('NICK ' + config.nick + '\r\n');
        client.write('USER dcpubot 0 * :Node bot\r\n');
        client.write('JOIN ' + config.channel + '\r\n');
    }
);

function assemble(code, callback) {
    code = code.replace(/\//g, '\n');
    console.log(code);
    request({
                uri: 'http://services.dcputoolcha.in/assemble',
                form: {file: code},
                method:' POST' 
            }, callback);
}

function msg(nick, channel, message) {
    if(channel != config.nick) {
        client.write("PRIVMSG " + channel + " :" + nick + ": " + message + "\r\n");
    } else {
        client.write("NOTICE " + nick + " :" + message + "\r\n");
    }
}

client.on('data', function(data) {
    message = data.toString();
    console.log(data.toString());

    matches = [];

    if((matches = message.match(/^PING :(.+)/))) {
        client.write('PONG :' + matches[1]);
        console.log('PONG :' + matches[1]);
    } else if((matches = message.match(/^:(.*)!.*PRIVMSG (#?[^ ]+) :>>>(.*)/))) {
        assemble(matches[3], function(error, response, body) {
            hex = [];
            result = JSON.parse(body).bytes;
	    for(var i = 0; i < result.length; i++) {
                hex.push(' 0x' + result[i].toString(16));
            }
	    console.log(hex);
            msg(matches[1], matches[2], hex);
        });
    }
});

client.on('end', function() {
    console.log('client disconnected');
});
