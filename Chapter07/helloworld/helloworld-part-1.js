var http = require("http")
var winston = require("winston")

var version = process.env.HELLOWORLD_VERSION 

var logger = new winston.Logger({ 
  transports: [new winston.transports.Console({ 
    timestamp: function() { 
       var d = new Date()
       return d.toISOString()
    }, 
  })] 
}) 

logger.rewriters.push(function(level, msg, meta) { 
  meta.version = version 
  return meta 
}) 

http.createServer(function (request, response) {

   // Send the HTTP header
   // HTTP Status: 200 : OK
   // Content Type: text/plain
   response.writeHead(200, {'Content-Type': 'text/plain'})

   // Send the response body as "Hello World"
   response.end('Hello World\n')
}).listen(3000)

// Console will print the message
logger.info("Server running") 
