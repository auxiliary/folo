// This file is required by the index.html file and will
// be executed in the renderer process for that window.
// All of the Node.js APIs are available in this process.

exec = require('child_process').exec;
net = require('net');

class Client
{
    constructor()
    {
        this.mode = 'variable';
        this.port = 5050;
    }

    run()
    {
        var self = this;
        this.server = net.createServer(function(socket){
            socket.on('data', function(data){
                let messages = String.fromCharCode.apply([], data);
                console.log(messages);

                if (self.mode == "variable")
                {
                    // the messages might end up having multiple dicts in it
                    // so we have to parse them out:
                    messages = messages.split('}');
                    messages = messages.splice(0, messages.length - 1);
                    messages = messages.map(function(m){ return JSON.parse(m + "}"); });
                    for (i in messages)
                    {
                        message = messages[i];
                        if (self.values.hasOwnProperty(message.varname))
                        {
                            self.values[message.varname].push(message.value);
                        }
                        else
                        {
                            self.values[message.varname] = [message.value];
                        }
                        self.visualize(message.varname);

                    }
                }

                // incoming line visualization messages
                else if (self.mode == "line")
                {
                    // the messages might end up having multiple dicts in it
                    // so we have to parse them out:
                    messages = messages.split('}');
                    messages = messages.splice(0, messages.length - 1);
                    messages = messages.map(function(m){ return JSON.parse(m + "}"); });
                    for (i in messages)
                    {
                        message = messages[i];
                        if (message.hasOwnProperty("file"))
                        {
                            if (message.file != self.last_filename || self.nodes.length == 0)
                                self.updateGraph(message);

                            self.last_filename = message.file;
                        }
                        else
                        {
                            message.file = self.last_filename;
                        }
                        self.highlight(message);
                        self.message_history.push(message);
                    }
                }

                /*
                self.graph_vis_timeout = setTimeout(function(){
                    self.updateGraphVis(); 
                    self.sequence_row += 1;
                    self.graph = { nodes: [], links: [] };
                    self.nodes = [];
                    console.log(self.sequence_row);
                }, 2000);
                */

                socket.write('OK');

            });
        }).listen(this.port);
        console.log("Running on " + this.port);
    }
}

document.querySelector(".btn-run").addEventListener("click", function(){
    exec("python -m trace variable " + this.config_filename + " " + filename);
});

client = Client();
client.run();

