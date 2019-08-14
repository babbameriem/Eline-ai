var restify = require('restify');
var builder = require('botbuilder');
const dialogflow = require('dialogflow');
const uuid = require('uuid');


//=========================================================
// Bot Setup
//=========================================================

// Setup Restify Server
var server = restify.createServer();
server.listen(process.env.port || process.env.PORT || 3978, function () {
   console.log('%s listening to %s', server.name, server.url); 
});
  
// Create chat bot
var connector = new builder.ChatConnector({
    appId: '',
    appPassword: ''
});

server.post('/api/messages', connector.listen());

//=========================================================
// Bots Dialogs
//=========================================================

// Create your bot with a function to receive messages from the user
var bot = new builder.UniversalBot(connector, async function (session) {
    var msg = session.message;
    if (msg.attachments && msg.attachments.length > 0) {
     var attachment = msg.attachments[0];
        var spawn = require('child_process').spawn,
    py    = spawn('path to your python environnment', ['all_data.py']),
    data = attachment.contentUrl,
    dataString = '';
setTimeout( function () {
py.stdout.on('data', function(data){
  dataString += data.toString();
});

py.stdout.on('end', function(){
  session.send(dataString);
});
py.stdin.write(JSON.stringify(data));
py.stdin.end();  }, 20000);


    } else {
        var utterance = msg.text;
            async function runSample(projectId = 'your project id') {
            // A unique identifier for the given session
            const sessionId = uuid.v4();

            // Create a new session
  	    const sessionClient = new dialogflow.SessionsClient({keyFilename:'path to your file .json'});
            const sessionPath = sessionClient.sessionPath(projectId, sessionId);

	    // The text query request.
            const request = {
                    session: sessionPath,
                    queryInput: {
                                text: {
                                    // The query to send to the dialogflow agent
        			    text: utterance ,
                                   // The language used by the client (fr-EU)
                                   languageCode: 'fr-EU',
                                     },
                                      },
                                };

           // Send request and log result
           const responses = await sessionClient.detectIntent(request);
           //console.log('Detected intent');
            const result = responses[0].queryResult;
            return session.send(result.fulfillmentText); }
 
          runSample();    
    }
});
