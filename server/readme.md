# Server <!-- omit from toc -->

- [v0.2](#v02)
  - [App communication](#app-communication)
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
  "boost": "false"
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
  "free_cars": [0, 1, 2, 3]
}
```

### Send data to move the car <!-- omit from toc -->

App sends:

```
{
  "action": "move_car",
  "car": 1,
  "move": "forward",
  "boost": "false"
}
```

Server responds:

```
{
  "status": "success"
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
  "car_status": {
    "car": 1,
    "battery_level": 85,
    "move": "forward",
    "boost": "false",
    "boost_value": 100
  }
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
    "time_remaining": 300
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
  "message": "Game started!"
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
  "status": "success"
}
```

## Server game management

The server will manage the game state, including the teams, scores, and time.

After the game starts, will start a count down timer for the game duration and start transmitting the car commands to the cars.

When the game is finished, no more commands will be sent to the cars. It will still be possible to get the game status and the car video feeds.

The server will buffer the video feeds from the cars and send them to the app when requested, but only keep the last frame for each car.

The server will also keep the last car command sent to each car, so that it can respond to the app when requested.