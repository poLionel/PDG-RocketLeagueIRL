# RLIRL Mobile App

This document provides comprehensive documentation for the RLIRL (Rocket League In Real Life) mobile application architecture and build instructions.

## Overview

The RLIRL mobile app is a .NET MAUI (Multi-platform App UI) application that serves as a remote controller for a physical Rocket League-style game with real cars. The app provides game management, car control, camera feeds, and real-time communication with the game server through WebSocket connections.

## Architecture

The application follows a clean layered architecture pattern with clear separation of concerns:

### 1. Presentation Layer (`RLIRL.App`)
- **Technology**: .NET MAUI with XAML
- **Pattern**: MVVM (Model-View-ViewModel)
- **Purpose**: User interface and interaction handling

#### Key Components:
- **Views**: XAML pages for different app screens
  - `WifiConnectPage` / `WifiSelector` - Network configuration
  - `MenuPage` - Main navigation
  - `GamePage` - Game control interface
  - `GameAdminPage` - Administrative game controls
  - `CarSelector` - Car selection interface

- **ViewModels**: Business logic for UI components
  - `WifiConnectViewModel` / `WifiSelectorViewModel` - WiFi management
  - `MenuViewModel` - Main menu logic
  - `GameViewModel` - Game control logic
  - `GameAdminViewModel` - Administrative controls
  - `CarSelectorViewModel` - Car selection logic

- **Helper Services**:
  - `ServiceHelper` - Dependency injection resolver for MAUI Shell

### 2. Business Logic Layer (`RLIRL.Business`)
- **Purpose**: Core business logic and domain services
- **Pattern**: Service-oriented architecture with dependency injection

#### Services:
- **`IGameService` / `GameService`**: Game state management, start/stop/pause/resume operations, score tracking
- **`ICarService` / `CarService`**: Car availability tracking, selection, and release management
- **`ICarControlService` / `CarControlService`**: Real-time car movement and control commands
- **`ICameraFeedService` / `CameraFeedService`**: Camera feed management and streaming
- **`ITimerService` / `TimerService`**: Game timing and countdown management

### 3. Server Communication Layer (`RLIRL.Server`)
- **Purpose**: WebSocket communication with the external game server
- **Pattern**: Command/Response pattern with background services

#### Key Components:

##### Background Services:
- **`ServerCommandSender`**: 
  - Continuously processes outgoing commands from a queue
  - Handles WebSocket connection pooling and automatic reconnection
  - Sends commands to the game server in real-time
  - Implements fault tolerance with automatic retry logic

- **`ServerResponseListener`**: 
  - Listens for incoming responses from the game server
  - Deserializes responses and routes them to appropriate processors
  - Uses reflection to dynamically map response types
  - Runs continuously in the background

##### Communication Infrastructure:
- **`IClientCommandQueue` / `ClientCommandQueue`**: Thread-safe command queuing system
- **`IWebSocketProvider` / `WebSocketProvider`**: WebSocket connection management
- **`IServerCommandSerializer` / `ServerCommandSerializer`**: Command/response serialization
- **`IServerConnectionStatusService`**: Connection status monitoring

##### Response Processing:
- **Response Processors**: Specialized handlers for each response type
  - `GetGameStatusResponseProcessor`
  - `GetFreeCarsResponseProcessor` 
  - `MoveCarResponseProcessor`
  - `SelectCarResponseProcessor`
  - And many more...

### 4. Abstractions Layer
- **`RLIRL.Business.Abstractions`**: Interfaces for business services
- **`RLIRL.Server.Abstractions`**: Interfaces for server communication

## Communication Flow

The application uses a unidirectional data flow pattern:

```
UI Layer (Views/ViewModels)
    ↓ (User actions)
Business Layer (Services)
    ↓ (Commands via IClientCommandQueue)
Server Layer (Background Services)
    ↓ (WebSocket)
External Game Server
    ↓ (WebSocket responses)
Server Layer (ServerResponseListener)
    ↓ (Processed responses)
Business Layer (Services)
    ↓ (Events/Notifications)
UI Layer (Property notifications via MVVM)
```

### Command Flow Example:
1. User presses "Start Game" button in `GamePage`
2. `GameViewModel` calls `IGameService.StartGame()`
3. `GameService` creates `StartGameCommand` and enqueues it via `IClientCommandQueue`
4. `ServerCommandSender` dequeues command and sends it via WebSocket
5. Game server processes command and sends `StartGameResponse`
6. `ServerResponseListener` receives response and routes to `StartGameResponseProcessor`
7. Processor updates `GameService` state
8. `GameService` raises `GameStatusChanged` event
9. `GameViewModel` updates UI through property notifications

## Background Services Deep Dive

### ServerCommandSender
- **Lifecycle**: Started in `MauiProgram.cs` and runs continuously
- **Threading**: Runs on background thread with cancellation token support
- **Reliability**: Implements connection pooling with automatic reconnection
- **Error Handling**: Logs exceptions and retries failed connections after delay

```csharp
// Key features:
- Processes commands from IClientCommandQueue
- Handles WebSocket connection lifecycle
- Implements retry logic with configurable delays
- Thread-safe operation with proper cancellation support
```

### ServerResponseListener
- **Lifecycle**: Started in `MauiProgram.cs` and runs continuously  
- **Threading**: Background processing with proper cancellation
- **Dynamic Routing**: Uses reflection to find response processors by command name attributes
- **Error Handling**: Comprehensive exception logging and fault tolerance

```csharp
// Key features:
- Listens for WebSocket responses continuously
- Dynamically maps responses to processors using attributes
- Processes responses asynchronously
- Maintains connection state and handles reconnection
```

## Configuration

### Server Configuration
Configuration is managed through JSON files and injected via `IOptions<ServerConfiguration>`:

- **Development**: `appsettings.Development.json`
  ```json
  {
    "ServerConfiguration": {
      "Host": "localhost",
      "Port": 8000
    }
  }
  ```

- **Production**: `appsettings.json`
  ```json
  {
    "ServerConfiguration": {
      "IsHostDefaultGateway": true,
      "Port": 8000
    }
  }
  ```

### Dependency Injection Setup
Services are registered in `MauiProgram.cs`:

```csharp
// Business services registration
builder.Services.RegisterBusiness(builder.Configuration);

// Server communication services
builder.Services.RegisterServer(builder.Configuration);

// Background services are started after app creation
var commandListener = app.Services.GetRequiredService<IServerResponseListener>();
commandListener.Start();

var commandSender = app.Services.GetRequiredService<IServerCommandSender>();
commandSender.Start();
```

## Build Instructions

### Prerequisites
- **.NET 9.0 SDK** or later
- **Visual Studio 2022 17.8+** with MAUI workload, or **VS Code** with C# extension
- **Platform-specific requirements**:
  - **Android**: Android SDK, Java 17
  - **iOS**: Xcode 15+, macOS
  - **Windows**: Windows 10 version 1809+ (for Windows target)

### Build Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/poLionel/PDG-RocketLeagueIRL.git
   cd PDG-RocketLeagueIRL/mobileApp
   ```

2. **Restore dependencies**
   ```bash
   dotnet restore
   ```

3. **Build the solution**
   ```bash
   # Build all projects
   dotnet build
   
   # Or build specific target framework
   dotnet build -f net9.0-android
   dotnet build -f net9.0-ios
   dotnet build -f net9.0-windows10.0.19041.0
   ```

4. **Run the application**
   ```bash
   # Android
   dotnet build -f net9.0-android && dotnet run -f net9.0-android
   
   # iOS (requires macOS)
   dotnet build -f net9.0-ios && dotnet run -f net9.0-ios
   
   # Windows
   dotnet build -f net9.0-windows10.0.19041.0 && dotnet run -f net9.0-windows10.0.19041.0
   ```

5. **For development with hot reload**
   ```bash
   dotnet watch run -f net9.0-android
   ```

### Testing

Run unit tests for business logic and server communication:

```bash
# Run all tests
dotnet test

# Run specific test project
dotnet test RLIRL.Business.Tests
dotnet test RLIRL.Server.Tests

# Run with coverage
dotnet test --collect:"XPlat Code Coverage"
```

## Development Setup

### IDE Configuration
- **Visual Studio**: Install MAUI workload and Android/iOS components
- **VS Code**: Install C# extension and .NET MAUI extension

### Debugging
- Use Visual Studio or VS Code debugger
- For network debugging, monitor WebSocket traffic
- Check application logs for background service status

### Hot Reload
MAUI supports hot reload for XAML and C# code changes during development.

## Troubleshooting

### Common Issues

1. **Build Errors**
   - Ensure .NET 9.0 SDK is installed
   - Verify MAUI workload installation: `dotnet workload list`
   - Install MAUI if missing: `dotnet workload install maui`

2. **WebSocket Connection Issues**
   - Check server configuration in `appsettings.json`
   - Verify game server is running and accessible
   - Review network connectivity and firewall settings

3. **Platform-Specific Issues**
   - **Android**: Ensure Android SDK and emulator are properly configured
   - **iOS**: Requires macOS and Xcode for building and deployment
   - **Windows**: Check Windows SDK version requirements

4. **Background Service Issues**
   - Monitor application logs for service startup errors
   - Verify dependency injection configuration
   - Check for proper service disposal on app shutdown

### Debugging Tips
- Enable debug logging in `appsettings.Development.json`
- Use Visual Studio diagnostic tools for memory and performance analysis
- Monitor WebSocket traffic with browser dev tools or network debugging tools
- Check device logs for platform-specific issues

## Contributing

When contributing to the mobile app:
1. Follow the existing architectural patterns
2. Add unit tests for new business logic
3. Update this documentation for architectural changes
4. Ensure proper error handling in background services
5. Follow MVVM patterns in the UI layer

## Related Documentation
- See `/docs/Workflow.md` for development workflow and branching strategy
- Check individual project READMEs for component-specific details
- Review server documentation for API contracts and WebSocket protocol