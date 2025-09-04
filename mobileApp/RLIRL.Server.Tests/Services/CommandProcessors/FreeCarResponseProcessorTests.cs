using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;
using RLIRL.Server.Services.CommandProcessors;
using Moq;
using Xunit;

namespace RLIRL.Server.Tests.Services.CommandProcessors
{
    public class FreeCarResponseProcessorTests
    {
        private readonly Mock<ICarService> _mockCarService;
        private readonly FreeCarResponseProcessor _processor;

        public FreeCarResponseProcessorTests()
        {
            _mockCarService = new Mock<ICarService>();
            _processor = new FreeCarResponseProcessor(_mockCarService.Object);
        }

        [Fact]
        public async Task ProcessResponseAsync_WhenCurrentCarDoesNotMatchResponseCar_UpdatesCurrentCarToNull()
        {
            // Arrange
            var currentCar = 1;
            var responseCar = 2;
            var response = new FreeCarResponse
            {
                Car = responseCar
            };

            _mockCarService.Setup(x => x.CurrentCar).Returns(currentCar);

            // Act
            await _processor.ProcessResponseAsync(response);

            // Assert
            _mockCarService.Verify(x => x.UpdateCurrentCar(null), Times.Once);
        }

        [Fact]
        public async Task ProcessResponseAsync_WhenCurrentCarMatchesResponseCar_DoesNotUpdateCurrentCar()
        {
            // Arrange
            var currentCar = 1;
            var responseCar = 1;
            var response = new FreeCarResponse
            {
                Car = responseCar
            };

            _mockCarService.Setup(x => x.CurrentCar).Returns(currentCar);

            // Act
            await _processor.ProcessResponseAsync(response);

            // Assert
            _mockCarService.Verify(x => x.UpdateCurrentCar(It.IsAny<int?>()), Times.Never);
        }

        [Fact]
        public async Task ProcessResponseAsync_WhenCurrentCarIsNull_UpdatesCurrentCarToNull()
        {
            // Arrange
            var response = new FreeCarResponse
            {
                Car = 1
            };

            _mockCarService.Setup(x => x.CurrentCar).Returns((int?)null);

            // Act
            await _processor.ProcessResponseAsync(response);

            // Assert
            _mockCarService.Verify(x => x.UpdateCurrentCar(null), Times.Once);
        }

        [Fact]
        public async Task ProcessResponseAsync_WithZeroResponseCar_WhenCurrentCarIsNotZero_UpdatesCurrentCarToNull()
        {
            // Arrange
            var currentCar = 5;
            var responseCar = 0;
            var response = new FreeCarResponse
            {
                Car = responseCar
            };

            _mockCarService.Setup(x => x.CurrentCar).Returns(currentCar);

            // Act
            await _processor.ProcessResponseAsync(response);

            // Assert
            _mockCarService.Verify(x => x.UpdateCurrentCar(null), Times.Once);
        }

        [Fact]
        public async Task ProcessResponseAsync_WithNegativeResponseCar_WhenCurrentCarIsDifferent_UpdatesCurrentCarToNull()
        {
            // Arrange
            var currentCar = 1;
            var responseCar = -1;
            var response = new FreeCarResponse
            {
                Car = responseCar
            };

            _mockCarService.Setup(x => x.CurrentCar).Returns(currentCar);

            // Act
            await _processor.ProcessResponseAsync(response);

            // Assert
            _mockCarService.Verify(x => x.UpdateCurrentCar(null), Times.Once);
        }

        [Fact]
        public async Task ProcessResponseAsync_CompletesSuccessfully()
        {
            // Arrange
            var response = new FreeCarResponse
            {
                Car = 1
            };

            _mockCarService.Setup(x => x.CurrentCar).Returns(2);

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
            var response = new FreeCarResponse
            {
                Car = 1
            };

            _mockCarService.Setup(x => x.CurrentCar).Returns(2);
            _mockCarService
                .Setup(x => x.UpdateCurrentCar(It.IsAny<int?>()))
                .Throws(expectedException);

            // Act & Assert
            var exception = await Assert.ThrowsAsync<InvalidOperationException>(
                () => _processor.ProcessResponseAsync(response));
            Assert.Same(expectedException, exception);
        }
    }
}