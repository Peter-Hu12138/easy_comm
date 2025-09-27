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
|room login request |0|
|DH public key from room host| 1|
|DH public key from room attendents|2|
|shared AES secrets sent over DH exchanged key|3|
|normal message over AES|4|
|room build request|5|
|room list request|6|


## Auth
Messages are authenticated by incoming ip and port; a JWT like method might be used in the future