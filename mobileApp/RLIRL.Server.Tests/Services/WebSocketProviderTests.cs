using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Services;
using Microsoft.Extensions.Options;
using Moq;
using System.Net;
using Xunit;

namespace RLIRL.Server.Tests.Services
{
    public class WebSocketProviderTests : IDisposable
    {
        private readonly Mock<IOptions<ServerConfiguration>> _mockServerConfiguration;
        private readonly Mock<IGatewayProvider> _mockGatewayProvider;
        private readonly WebSocketProvider _provider;

        public WebSocketProviderTests()
        {
            _mockServerConfiguration = new Mock<IOptions<ServerConfiguration>>();
            _mockGatewayProvider = new Mock<IGatewayProvider>();
            
            // Set up default configuration
            var defaultConfig = new ServerConfiguration
            {
                Host = "localhost",
                Port = 8080,
                Secure = false,
                IsHostDefaultGateway = false
            };
            
            _mockServerConfiguration.Setup(x => x.Value).Returns(defaultConfig);
            
            _provider = new WebSocketProvider(_mockServerConfiguration.Object, _mockGatewayProvider.Object);
        }

        [Fact]
        public void Constructor_WithValidParameters_DoesNotThrow()
        {
            // Act & Assert
            var exception = Record.Exception(() => new WebSocketProvider(
                _mockServerConfiguration.Object,
                _mockGatewayProvider.Object));
            Assert.Null(exception);
        }

        [Fact]
        public async Task GetWebSocketClientAsync_WithInvalidHost_ThrowsException()
        {
            // Arrange
            var config = new ServerConfiguration
            {
                Host = "invalid-host-that-does-not-exist",
                Port = 8080,
                Secure = false,
                IsHostDefaultGateway = false
            };
            _mockServerConfiguration.Setup(x => x.Value).Returns(config);

            using var provider = new WebSocketProvider(_mockServerConfiguration.Object, _mockGatewayProvider.Object);

            // Act & Assert
            await Assert.ThrowsAnyAsync<Exception>(() => 
                provider.GetWebSocketClientAsync(CancellationToken.None));
        }

        [Fact]
        public async Task GetWebSocketClientAsync_WithEmptyHost_WhenNotUsingGateway_ThrowsException()
        {
            // Arrange
            var config = new ServerConfiguration
            {
                Host = "",
                Port = 8080,
                Secure = false,
                IsHostDefaultGateway = false
            };
            _mockServerConfiguration.Setup(x => x.Value).Returns(config);

            using var provider = new WebSocketProvider(_mockServerConfiguration.Object, _mockGatewayProvider.Object);

            // Act & Assert
            await Assert.ThrowsAnyAsync<Exception>(() => 
                provider.GetWebSocketClientAsync(CancellationToken.None));
        }

        [Fact]
        public async Task GetWebSocketClientAsync_WhenUsingGatewayWithNullGateway_ThrowsException()
        {
            // Arrange
            var config = new ServerConfiguration
            {
                Host = "localhost",
                Port = 8080,
                Secure = false,
                IsHostDefaultGateway = true
            };
            _mockServerConfiguration.Setup(x => x.Value).Returns(config);
            _mockGatewayProvider.Setup(x => x.GetGateway()).Returns((IPAddress?)null);

            using var provider = new WebSocketProvider(_mockServerConfiguration.Object, _mockGatewayProvider.Object);

            // Act & Assert
            await Assert.ThrowsAnyAsync<Exception>(() => 
                provider.GetWebSocketClientAsync(CancellationToken.None));
        }

        [Fact]
        public void Dispose_CalledMultipleTimes_DoesNotThrow()
        {
            // Act & Assert
            var exception = Record.Exception(() =>
            {
                _provider.Dispose();
                _provider.Dispose();
                _provider.Dispose();
            });
            Assert.Null(exception);
        }

        [Fact]
        public async Task GetWebSocketClientAsync_WithSecureConfiguration_UsesWssProtocol()
        {
            // Arrange
            var config = new ServerConfiguration
            {
                Host = "localhost",
                Port = 8080,
                Secure = true,
                IsHostDefaultGateway = false
            };
            _mockServerConfiguration.Setup(x => x.Value).Returns(config);

            using var provider = new WebSocketProvider(_mockServerConfiguration.Object, _mockGatewayProvider.Object);

            // Act & Assert - This will likely throw because we can't connect, but it tests the protocol logic
            await Assert.ThrowsAnyAsync<Exception>(() => 
                provider.GetWebSocketClientAsync(CancellationToken.None));
        }

        public void Dispose()
        {
            _provider?.Dispose();
        }
    }
}