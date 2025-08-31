# Server <!-- omit from toc -->

- [v0.2](#v02)
  - [App communication](#app-communication)
    - [Return data from the server](#return-data-from-the-server)
  - [Car communication](#car-communication)
    - [Bluetooth Low Energy (BLE)](#bluetooth-low-energy-ble)
- [v0.3](#v03)
  - [App communication](#app-communication-1)
  - [Car communication](#car-communication-1)
    - [Bluetooth Low Energy (BLE)](#bluetooth-low-energy-ble-1)
    - [Websocket send video feed](#websocket-send-video-feed)
  - [Server game management](#server-game-management)

# v0.2

## App communication

We will use a websocket to communicate with the app.

Use JSONs to send data.

### Send data to move the car <!-- omit from toc -->

```
{
  "action": "move_car",
  "car": 1,
  "move": "forward",
  "x": 0,
  "boost": "false"
}
```

- `move`: Movement direction - "forward", "backward", or "stopped"
- `x`: Steering value from -100 (full left) to 100 (full right), 0 is straight

### Return data from the server

```
{
  "status": "success",
  "action": "move_car"
}
```

## Car communication

### Bluetooth Low Energy (BLE)

We will use BLE to automatically pair the car with the server.

We will also use BLE to send the commands (move, boost) from the server to the car.

# v0.3

## App communication

We will use a websocket to communicate with the app.

Use JSONs to send data.

### Get free cars <!-- omit from toc -->

App sends:

```
{
  "action": "get_free_cars"
}
```

Server responds:

```
{
  "status": "success",
  "action": "get_free_cars",
  "free_cars": [0, 1, 2, 3]
}
```

### Select a car <!-- omit from toc -->

App sends:

```
{
  "action": "select_car",
  "car": 1
}
```

Server responds:

```
{
  "status": "success",
  "action": "select_car",
  "car": 1
}
```

### Free a car <!-- omit from toc -->

App sends:

```
{
  "action": "free_car",
  "car": 1
}
```

Server responds:

```
{
  "status": "success",
  "action": "free_car",
  "car": 1
}
```

### Send data to move the car <!-- omit from toc -->

App sends:

```
{
  "action": "move_car",
  "car": 1,
  "move": "forward",
  "x": 0,
  "boost": "false"
}
```

- `move`: Movement direction - "forward", "backward", or "stopped"
- `x`: Steering value from -100 (full left) to 100 (full right), 0 is straight

Server responds:

```
{
  "status": "success",
  "action": "move_car"
}
```

### Get car status <!-- omit from toc -->

App sends:

```
{
  "action": "get_car_status",
  "car": 1
}
```

Server responds:

```
{
  "status": "success",
  "action": "get_car_status",
  "car": 1,
  "battery_level": 85,
  "move": "forward",
  "x": 0,
  "boost": "false",
  "boost_value": 100
}
```

### Get accessible car feeds <!-- omit from toc -->

App sends:

```
{
  "action": "get_accessible_car_feeds"
}
```

Server responds:

```
{
  "status": "success",
  "action": "get_accessible_car_feeds",
  "accessible_feeds": [0, 1, 2, 3]
}
```

### Get car video feed <!-- omit from toc -->

App sends:

```
{
  "action": "get_car_video_feed",
  "car": 1
}
```

Server responds with a jpeg of the last frame.

### A goal is scored <!-- omit from toc -->

App sends:

```
{
  "action": "goal_scored",
  "team": "red"
}
```

Server responds:

```
{
  "status": "success",
  "action": "goal_scored",
  "message": "Goal scored by red team!"
}
```

### Get game status <!-- omit from toc -->

App sends:

```
{
  "action": "get_game_status"
}
```

Server responds:

```
{
  "status": "success",
  "action": "get_game_status",
  "game_status": {
    "teams": {
      "red": {
        "score": 1,
        "cars": [0, 1]
      },
      "blue": {
        "score": 0,
        "cars": [2, 3]
      }
    },
    "time_remaining": 300,
    "elapsed_time": 120,
    "state": "active",
    "match_length_seconds": 300,
    "start_date": "2025-08-29T14:30:00.123456",
    "total_paused_time": 0,
    "is_active": true,
    "is_finished": false
  }
}
```

### Start the game <!-- omit from toc -->

App sends:

```
{
  "action": "start_game"
}
```

Server responds:

```
{
  "status": "success",
  "action": "start_game",
  "message": "Game started!"
}
```

### Stop the game <!-- omit from toc -->

App sends:

```
{
  "action": "stop_game"
}
```

Server responds:

```
{
  "status": "success",
  "action": "stop_game",
  "message": "Game stopped!"
}
```

### Resume the game <!-- omit from toc -->

App sends:

```
{
  "action": "resume_game"
}
```

Server responds:

```
{
  "status": "success",
  "action": "resume_game",
  "message": "Game resumed!"
}
```

### End the game <!-- omit from toc -->

App sends:

```
{
  "action": "end_game"
}
```

Server responds:

```
{
  "status": "success",
  "action": "end_game",
  "message": "Game ended!"
}
```

### Add team <!-- omit from toc -->

App sends:

```
{
  "action": "add_team",
  "color": "green"
}
```

Server responds:

```
{
  "status": "success",
  "action": "add_team",
  "message": "Team 'Green Team' added successfully"
}
```

### Add car to team <!-- omit from toc -->

App sends:

```
{
  "action": "add_car_to_team",
  "car_id": 2,
  "team": "red"
}
```

Server responds:

```
{
  "status": "success",
  "action": "add_car_to_team",
  "message": "Car 2 added to red team"
}
```

### Remove car from teams <!-- omit from toc -->

App sends:

```
{
  "action": "remove_car_from_teams",
  "car_id": 2
}
```

Server responds:

```
{
  "status": "success",
  "action": "remove_car_from_teams",
  "message": "Car 2 removed from all teams"
}
```

## Car communication

### Bluetooth Low Energy (BLE)

We will use BLE to automatically pair the car with the server.

We will also use BLE to send the commands (move, boost) from the server to the car.

### Websocket send video feed

The car will send the video feed to the server using a websocket.

Car sends:

```
{
  "action": "send_video_feed",
  "car": 1,
  "video_frame": "<base64_encoded_jpeg>"
}
```

Server responds:

```
{
  "status": "success",
  "action": "send_video_feed"
}
```

## Server game management

The server will manage the game state, including the teams, scores, and time.

After the game starts, will start a count down timer for the game duration and start transmitting the car commands to the cars.

When the game is finished, no more commands will be sent to the cars. It will still be possible to get the game status and the car video feeds.

The server will buffer the video feeds from the cars and send them to the app when requested, but only keep the last frame for each car.

The server will also keep the last car command sent to each car, so that it can respond to the app when requested.