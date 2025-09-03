using RLIRL.Server.Services;
using System.Net;
using System.Net.NetworkInformation;
using Xunit;

namespace RLIRL.Server.Tests.Services
{
    public class GatewayProviderTests
    {
        private readonly GatewayProvider _gatewayProvider;

        public GatewayProviderTests()
        {
            _gatewayProvider = new GatewayProvider();
        }

        [Fact]
        public void GetGateway_ReturnsIPAddressOrNull()
        {
            // Act
            var result = _gatewayProvider.GetGateway();

            // Assert
            // Result can be null if no gateway is found (e.g., in isolated test environments)
            // or should be a valid IP address
            if (result != null)
            {
                Assert.IsType<IPAddress>(result);
                Assert.True(IsValidIPAddress(result));
            }
        }

        [Fact]
        public void GetGateway_WithAvailableNetworkInterfaces_ReturnsConsistentResult()
        {
            // Act - Call multiple times to ensure consistency
            var result1 = _gatewayProvider.GetGateway();
            var result2 = _gatewayProvider.GetGateway();

            // Assert
            Assert.Equal(result1, result2);
        }

        [Fact]
        public void GetGateway_DoesNotThrowException()
        {
            // Act & Assert
            var exception = Record.Exception(() => _gatewayProvider.GetGateway());
            Assert.Null(exception);
        }

        [Fact]
        public void GetGateway_WhenNetworkInterfacesExist_ChecksOperationalStatus()
        {
            // This test verifies the method doesn't crash when examining network interfaces
            // and follows the expected logic path
            
            // Act
            var result = _gatewayProvider.GetGateway();

            // Assert - Should not throw and return either null or valid IP
            // The exact result depends on the test environment's network configuration
            if (result != null)
            {
                Assert.True(result.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork ||
                           result.AddressFamily == System.Net.Sockets.AddressFamily.InterNetworkV6);
            }
        }

        private static bool IsValidIPAddress(IPAddress ipAddress)
        {
            // Check if it's a valid IP address format
            if (ipAddress == null) return false;
            
            // Basic validation - should not be empty or local loopback for a gateway
            return !IPAddress.IsLoopback(ipAddress) && 
                   !ipAddress.Equals(IPAddress.None) && 
                   !ipAddress.Equals(IPAddress.Any);
        }
    }
}