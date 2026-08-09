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
|shared AES secrets sent over DH exchanged key|5|
|normal message over AES|6|
|room build request|7|
|room list request|8|

### Implemented payloads (types 1-5 and 8 are reserved, not implemented yet)

0 (room login request): `room_name + ',' + password`

7 (room build request): same payload as type 0; creates the room and admits the creator.

The server answers a type 0/7 request with a frame of the same type byte whose
payload is `ok,room_name` or `fail,reason`.

6 (normal message): `room_name + ',' + text`; relayed to every other member of
that room (unauth messages will be ignored).


## Auth
Messages are authenticated by incoming ip and port; a JWT like method might be used in the future