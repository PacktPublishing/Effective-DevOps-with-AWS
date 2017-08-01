[![Build Status](https://travis-ci.org/pkallos/winston-firehose.svg?branch=master)](https://travis-ci.org/pkallos/winston-firehose)

# winston-firehose 

NodeJS module, winston logging transport which writes to AWS Firehose.

## Usage

You can add this logger transport with the following code:

```javascript
var winston = require('winston');
var WFirehose = require('winston-firehose');

// register the transport
var logger = new (winston.Logger)({
    transports: [
      new WFirehose({
        'streamName': 'firehose_stream_name',
        'firehoseOptions': {
          'region': 'us-east-1'
        }
      })
    ]
  });
  
// log away!!
// with just a string
logger.info('This is the log message!');

// or with meta info
logger.info('This is the log message!', { snakes: 'delicious' }); 
```

This will write messages as strings (using JSON.stringify) into Firehose in the following format:
```
{
  timestamp: 2016-05-20T22:48:01.106Z,
  level: "info",
  message: "This is the log message!",
  meta: { snakes: "delicious" }
};
```

## Options

`streamName (string) - required` The name of the Firehose stream to write to.

`firehoseOptions (object) - optional/suggested` The Firehose options that are passed directly to the constructor,
 [documented by AWS here](http://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/Firehose.html#constructor-property)

## Details

At the moment this logger sends (unacknowledged!) log messages into firehose. Right now the behavior if the log
message fails to write to Firehose is simply to do absolutely nothing and fail silently.
