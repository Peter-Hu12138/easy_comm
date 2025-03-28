# easy_comm

## Deployment to server
1. Download `chat_s.py`
2. `python /(path_to_chat_s.py)/chat_s.py port_to_listen_to`

## Client
1. Download `chat_flex.py`
2. `python /(path_to_chat_flex.py)/chat_flex.py server_ip port_to_connect_to name_in_chat_room`

## Design
In server side, I maintained a dictionary that maps from unique identifier of chat session (string) to a list authenticated members represented by socket sessions.