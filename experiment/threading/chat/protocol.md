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
|DH public key from client|1|
|DH public key from main chat process|2|
|DH public key from room host|3|
|DH public key from room attendents|4|
|shared AES secrets sent over DH exchanged key|4|
|normal message over AES|5| 
|room build request|6|
|room list request|7|

5: what follows the first byte is a comma delimited string name for chat room name (unauth messages will be ignored)
6: has additional info whether to amke room public thru room list request


## Auth
Messages are authenticated by incoming ip and port; a JWT like method might be used in the future