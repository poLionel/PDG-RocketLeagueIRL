using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;
using RLIRL.Server.Services.CommandProcessors;
using Moq;
using Xunit;

namespace RLIRL.Server.Tests.Services.CommandProcessors
{
    public class GetFreeCarsResponseProcessorTests
    {
        private readonly Mock<ICarService> _mockCarService;
        private readonly GetFreeCarsResponseProcessor _processor;

        public GetFreeCarsResponseProcessorTests()
        {
            _mockCarService = new Mock<ICarService>();
            _processor = new GetFreeCarsResponseProcessor(_mockCarService.Object);
        }

        [Fact]
        public async Task ProcessResponseAsync_WithValidResponse_CallsUpdateFreeCars()
        {
            // Arrange
            var freeCars = new int[] { 1, 2, 3 };
            var response = new GetFreeCarsResponse
            {
                FreeCars = freeCars
            };

            // Act
            await _processor.ProcessResponseAsync(response);

            // Assert
            _mockCarService.Verify(x => x.UpdateFreeCars(freeCars), Times.Once);
        }

        [Fact]
        public async Task ProcessResponseAsync_WithEmptyFreeCars_CallsUpdateFreeCars()
        {
            // Arrange
            var freeCars = new int[0];
            var response = new GetFreeCarsResponse
            {
                FreeCars = freeCars
            };

            // Act
            await _processor.ProcessResponseAsync(response);

            // Assert
            _mockCarService.Verify(x => x.UpdateFreeCars(freeCars), Times.Once);
        }

        [Fact]
        public async Task ProcessResponseAsync_WithNullFreeCars_CallsUpdateFreeCars()
        {
            // Arrange
            var response = new GetFreeCarsResponse
            {
                FreeCars = null!
            };

            // Act
            await _processor.ProcessResponseAsync(response);

            // Assert
            _mockCarService.Verify(x => x.UpdateFreeCars(null!), Times.Once);
        }

        [Fact]
        public async Task ProcessResponseAsync_CompletesSuccessfully()
        {
            // Arrange
            var response = new GetFreeCarsResponse
            {
                FreeCars = new int[] { 1, 2 }
            };

            // Act
            var task = _processor.ProcessResponseAsync(response);

            // Assert
            Assert.True(task.IsCompletedSuccessfully);
            await task; // Should not throw
        }

        [Fact]
        public async Task ProcessResponseAsync_WhenCarServiceThrows_PropagatesException()
        {
            // Arrange
            var expectedException = new InvalidOperationException("Car service error");
            var response = new GetFreeCarsResponse
            {
                FreeCars = new int[] { 1 }
            };

            _mockCarService
                .Setup(x => x.UpdateFreeCars(It.IsAny<IEnumerable<int>>()))
                .Throws(expectedException);

            // Act & Assert
            var exception = await Assert.ThrowsAsync<InvalidOperationException>(
                () => _processor.ProcessResponseAsync(response));
            Assert.Same(expectedException, exception);
        }
    }
}