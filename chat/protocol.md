# Technical details
The server app is in essence a smart multiplexer that doesn't store messages and secrets and only handle relay of messages based on a simple room name-password manner.

The messages are received in buffer and processed after receiving is done in full. Also note that this will be changed to a 

## message format
delimiter: \x03 // end of text

********
| type |

| contents |
********


### Message type byte
This byte is reserved to indicate meta data about this message; right now, here are they:

| type | byte |
|------|------|
|create room request |0|
|join room request|1|
|leave room request|2|
|Text chat message|3|
|Image chat message|4|
|Other file chat message|5|

Every message on tcp starts with a variable length prefix truncated in a unit of 4 bytes: the most significant bit having a value of 1 means we need to read next byte, recursively. After all prefix bytes are read, we remove the most significant bit in all the 4 byte unit and cat them together in big endian: what was received first was more significant.

After prefix is fully read, read the number bytes the prefix designates, and all the message has this format:
| bbbbbbbb | first byte has the type info
| bbbbbbbb |
| bbbbbbbb |
      .
      .
      .
| bbbbbbbb |
| bbbbbbbb | the rest of bytes form a json message (including file transfer as files are transmitted as text encoded in BASE64)

## Auth
Messages are authenticated by incoming ip and port; a JWT like method might be used in the future.
