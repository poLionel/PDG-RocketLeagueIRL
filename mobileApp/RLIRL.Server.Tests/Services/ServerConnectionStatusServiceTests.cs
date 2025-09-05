using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Services;
using Moq;
using System.Net.WebSockets;
using Xunit;

namespace RLIRL.Server.Tests.Services
{
    public class ServerConnectionStatusServiceTests
    {
        private readonly Mock<IWebSocketProvider> _mockWebSocketProvider;
        private readonly ServerConnectionStatusService _service;

        public ServerConnectionStatusServiceTests()
        {
            _mockWebSocketProvider = new Mock<IWebSocketProvider>();
            _service = new ServerConnectionStatusService(_mockWebSocketProvider.Object);
        }

        [Fact]
        public async Task IsServerConnectedAsync_WhenWebSocketConnectionSucceeds_ReturnsTrue()
        {
            // Arrange
            // Create a real ClientWebSocket since we can't mock sealed classes
            // The service only checks if GetWebSocketClientAsync succeeds, it doesn't use the WebSocket
            using var realWebSocket = new ClientWebSocket();
            _mockWebSocketProvider
                .Setup(x => x.GetWebSocketClientAsync(It.IsAny<CancellationToken>()))
                .ReturnsAsync(realWebSocket);

            // Act
            var result = await _service.IsServerConnectedAsync();

            // Assert
            Assert.True(result);
            _mockWebSocketProvider.Verify(x => x.GetWebSocketClientAsync(CancellationToken.None), Times.Once);
        }

        [Fact]
        public async Task IsServerConnectedAsync_WhenWebSocketThrowsWebSocketException_ReturnsFalse()
        {
            // Arrange
            _mockWebSocketProvider
                .Setup(x => x.GetWebSocketClientAsync(It.IsAny<CancellationToken>()))
                .ThrowsAsync(new WebSocketException("Connection failed"));

            // Act
            var result = await _service.IsServerConnectedAsync();

            // Assert
            Assert.False(result);
            _mockWebSocketProvider.Verify(x => x.GetWebSocketClientAsync(CancellationToken.None), Times.Once);
        }

        [Fact]
        public async Task IsServerConnectedAsync_WhenWebSocketThrowsOtherException_ThrowsException()
        {
            // Arrange
            var expectedException = new InvalidOperationException("Some other error");
            _mockWebSocketProvider
                .Setup(x => x.GetWebSocketClientAsync(It.IsAny<CancellationToken>()))
                .ThrowsAsync(expectedException);

            // Act & Assert
            var exception = await Assert.ThrowsAsync<InvalidOperationException>(
                () => _service.IsServerConnectedAsync());
            Assert.Same(expectedException, exception);
        }

        [Fact]
        public async Task IsServerConnectedAsync_WithCancellationToken_PassesTokenToProvider()
        {
            // Arrange
            var cancellationToken = new CancellationToken();
            using var realWebSocket = new ClientWebSocket();
            _mockWebSocketProvider
                .Setup(x => x.GetWebSocketClientAsync(cancellationToken))
                .ReturnsAsync(realWebSocket);

            // Act
            var result = await _service.IsServerConnectedAsync(cancellationToken);

            // Assert
            Assert.True(result);
            _mockWebSocketProvider.Verify(x => x.GetWebSocketClientAsync(cancellationToken), Times.Once);
        }

        [Fact]
        public async Task IsServerConnectedAsync_WhenCancellationRequested_ThrowsOperationCanceledException()
        {
            // Arrange
            using var cts = new CancellationTokenSource();
            cts.Cancel();
            
            _mockWebSocketProvider
                .Setup(x => x.GetWebSocketClientAsync(It.IsAny<CancellationToken>()))
                .ThrowsAsync(new OperationCanceledException());

            // Act & Assert
            await Assert.ThrowsAsync<OperationCanceledException>(
                () => _service.IsServerConnectedAsync(cts.Token));
        }

        [Fact]
        public async Task IsServerConnectedAsync_CalledMultipleTimes_CallsProviderEachTime()
        {
            // Arrange
            using var realWebSocket = new ClientWebSocket();
            _mockWebSocketProvider
                .Setup(x => x.GetWebSocketClientAsync(It.IsAny<CancellationToken>()))
                .ReturnsAsync(realWebSocket);

            // Act
            await _service.IsServerConnectedAsync();
            await _service.IsServerConnectedAsync();
            await _service.IsServerConnectedAsync();

            // Assert
            _mockWebSocketProvider.Verify(x => x.GetWebSocketClientAsync(CancellationToken.None), Times.Exactly(3));
        }
    }
}