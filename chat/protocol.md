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
|room build request|1|
|room list request|2|
|DH public key from room host (auth and forwarding to attendent)|3|
|DH public key from room attendents (auth and forwarding to room host)|4|
|shared AES secrets sent over DH exchanged key|5|
|normal chat room message (end to end encrypted, forwarding is all one needs) |6|
|TLS reserved|7|

0: type_byte + room_name + ',' + password.;
1: has additional info whether to amke room public thru room list request
6: what follows the first byte is a comma delimited string name for chat room name (unauth messages will be ignored)


## Auth
Messages are authenticated by incoming ip and port; a JWT like method might be used in the future