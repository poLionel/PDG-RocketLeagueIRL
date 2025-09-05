using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;
using RLIRL.Server.Services;
using Microsoft.Extensions.Logging;
using Moq;
using System.Net.WebSockets;
using Xunit;

namespace RLIRL.Server.Tests.Services
{
    public class ServerCommandSenderTests
    {
        private readonly Mock<IWebSocketProvider> _mockWebSocketProvider;
        private readonly Mock<IClientCommandQueue> _mockCommandQueue;
        private readonly Mock<IServerCommandSerializer> _mockSerializer;
        private readonly Mock<ILogger<ServerCommandSender>> _mockLogger;
        private readonly ServerCommandSender _service;

        public ServerCommandSenderTests()
        {
            _mockWebSocketProvider = new Mock<IWebSocketProvider>();
            _mockCommandQueue = new Mock<IClientCommandQueue>();
            _mockSerializer = new Mock<IServerCommandSerializer>();
            _mockLogger = new Mock<ILogger<ServerCommandSender>>();
            _service = new ServerCommandSender(
                _mockWebSocketProvider.Object,
                _mockCommandQueue.Object,
                _mockSerializer.Object,
                _mockLogger.Object);
        }

        [Fact]
        public void Start_WhenCalled_DoesNotThrow()
        {
            // Act & Assert
            var exception = Record.Exception(() => _service.Start());
            Assert.Null(exception);
        }

        [Fact]
        public void Stop_WhenCalled_DoesNotThrow()
        {
            // Act & Assert
            var exception = Record.Exception(() => _service.Stop());
            Assert.Null(exception);
        }

        [Fact]
        public void Start_CalledMultipleTimes_DoesNotThrow()
        {
            // Act & Assert
            var exception = Record.Exception(() =>
            {
                _service.Start();
                _service.Start();
                _service.Start();
            });
            Assert.Null(exception);
        }

        [Fact]
        public void Stop_CalledMultipleTimes_DoesNotThrow()
        {
            // Act & Assert
            var exception = Record.Exception(() =>
            {
                _service.Stop();
                _service.Stop();
                _service.Stop();
            });
            Assert.Null(exception);
        }

        [Fact]
        public void StartAndStop_CalledInSequence_DoesNotThrow()
        {
            // Act & Assert
            var exception = Record.Exception(() =>
            {
                _service.Start();
                _service.Stop();
                _service.Start();
                _service.Stop();
            });
            Assert.Null(exception);
        }

        [Fact]
        public async Task Start_WithWebSocketFailure_DoesNotThrow()
        {
            // Arrange
            _mockWebSocketProvider
                .Setup(x => x.GetWebSocketClientAsync(It.IsAny<CancellationToken>()))
                .ThrowsAsync(new WebSocketException("Connection failed"));

            // Act & Assert
            var exception = Record.Exception(() => _service.Start());
            Assert.Null(exception);

            // Give some time for the background task to attempt connection
            await Task.Delay(100);

            // Should not throw even with connection failures
            _service.Stop();
        }

        [Fact]
        public void Constructor_WithValidParameters_DoesNotThrow()
        {
            // Act & Assert
            var exception = Record.Exception(() => new ServerCommandSender(
                _mockWebSocketProvider.Object,
                _mockCommandQueue.Object,
                _mockSerializer.Object,
                _mockLogger.Object));
            Assert.Null(exception);
        }
    }
}