# PDG-RocketLeagueIRL

A real-world implementation of Rocket League using remote-controlled cars with real-time game management and mobile control interfaces.

**Live Demo:** https://polionel.github.io/PDG-RocketLeagueIRL/

## Project Overview

PDG-RocketLeagueIRL brings the popular video game Rocket League into the physical world. Players control real RC cars on a physical field to play soccer, complete with live scoring, game management, and spectator features.

### Key Features

- **Real-time Car Control**: Control RC cars through mobile app with precision steering and boost capabilities
- **Cross-platform Mobile App**: .NET MAUI application for iOS and Android
- **WebSocket Communication**: Real-time bidirectional communication between app, server, and cars
- **Bluetooth Integration**: Direct car communication via BLE for low-latency control
- **Live Camera Feeds**: Real-time video streaming from car-mounted cameras
- **Game Management**: Complete match management with scoring, timing, and administration
- **Multi-player Support**: Support for multiple cars and players simultaneously
- **Spectator Mode**: Live match viewing with real-time score updates

## Architecture

```
PDG-RocketLeagueIRL/
├── server/          # Python WebSocket server & game management
├── cars/            # Embedded firmware (PlatformIO/Arduino)
├── mobileApp/       # .NET MAUI cross-platform mobile app
├── landingPage/     # Project website and documentation
└── docs/           # Project documentation and specifications
```

### System Components

#### Server (`/server`)
- **Technology**: Python with asyncio, WebSocket, and Bluetooth
- **Purpose**: Central game management, car coordination, and real-time communication
- **Features**:
  - WebSocket server for mobile app communication
  - Bluetooth Low Energy (BLE) car communication
  - Game state management and scoring
  - Auto-provisioning and device discovery
  - Docker containerization support

#### Cars (`/cars`)
- **Technology**: PlatformIO/Arduino (ESP32-based)
- **Purpose**: Physical car control and sensor integration
- **Features**:
  - Motor control and steering
  - Camera integration
  - Bluetooth connectivity
  - Battery management
  - WiFi provisioning

#### Mobile App (`/mobileApp`)
- **Technology**: .NET MAUI (C#)
- **Purpose**: User interface for game control and management
- **Architecture**: Clean layered architecture with MVVM pattern
- **Features**:
  - Car selection and control
  - Game administration
  - Real-time match viewing
  - WiFi configuration
  - Cross-platform compatibility (iOS/Android)

#### Landing Page (`/landingPage`)
- **Technology**: HTML, CSS, JavaScript
- **Purpose**: Project showcase and documentation website
- **Features**: Bootstrap-based responsive design

## Quick Start

### Prerequisites

- **For Server**: Python 3.8+, Docker (optional)
- **For Mobile App**: .NET 6+, Visual Studio or VS Code
- **For Cars**: PlatformIO, ESP32 development board
- **For Development**: Git, modern web browser

### 1. Server Setup

```bash
cd server
pip install -r requirements.txt
python main.py
```

Or using Docker:
```bash
cd server
docker-compose up
```

### 2. Mobile App Setup

```bash
cd mobileApp
dotnet restore
dotnet build
# For Android
dotnet build -f net6.0-android
# For iOS
dotnet build -f net6.0-ios
```

### 3. Car Firmware Setup

```bash
cd cars/firmware
pio run
pio upload
```

## User Personas

Our project serves multiple user types:

- **Rocket League Players**: Experienced gamers seeking physical gameplay
- **New Players**: Newcomers discovering the concept for the first time
- **Referees**: Match administrators managing game flow and rules
- **Spectators**: Audience members following matches live
- **Developers**: Contributors extending and maintaining the project

## Development Workflow

We follow a Git-flow branching strategy:

- **`main`**: Production-ready releases
- **`develop`**: Integration branch for ongoing development
- **`feature/*`**: New feature development
- **`release/*`**: Release preparation and stabilization
- **`hotfix/*`**: Critical production fixes

### Version Control

- **Semantic Versioning**: `vMAJOR.MINOR.PATCH` (e.g., v1.2.3)
- **Automated CI/CD**: Triggered on tagged releases
- **Pull Request Reviews**: Required for all changes

## Communication Protocols

### WebSocket API
- **App ↔ Server**: JSON-based real-time communication
- **Commands**: Car movement, game state, administration
- **Responses**: Game updates, car status, match events

### Bluetooth Low Energy (BLE)
- **Server ↔ Cars**: Low-latency direct control
- **Services**: Motor control, camera, sensors, battery
- **Auto-discovery**: Automatic car detection and pairing

## Technology Stack

| Component | Technologies |
|-----------|-------------|
| **Backend** | Python, asyncio, WebSocket, Bluetooth |
| **Mobile** | .NET MAUI, C#, XAML, MVVM |
| **Embedded** | PlatformIO, Arduino, ESP32, C++ |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap |
| **Infrastructure** | Docker, Git, CI/CD |

## Documentation

- **[User Stories & Personas](docs/Personas_users_stories.md)**: Detailed user requirements
- **[Development Workflow](docs/Workflow.md)**: Git strategy and development process
- **[Server Documentation](server/readme.md)**: API specifications and setup
- **[Mobile App Documentation](mobileApp/README.md)**: Architecture and build instructions
- **[Car Design Documentation](cars/docs/)**: Hardware and firmware specifications

## Contributing

We welcome contributions! Please see our development workflow documentation and feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is part of a academic coursework (PDG - Projet de Groupe).

## Demonstration

Check out our live demonstration and project showcase at: https://polionel.github.io/PDG-RocketLeagueIRL/

---

**Built with love by the PDG-RocketLeagueIRL Team**
