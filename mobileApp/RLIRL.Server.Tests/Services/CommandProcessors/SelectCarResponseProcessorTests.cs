using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;
using RLIRL.Server.Services.CommandProcessors;
using Moq;
using Xunit;

namespace RLIRL.Server.Tests.Services.CommandProcessors
{
    public class SelectCarResponseProcessorTests
    {
        private readonly Mock<ICarService> _mockCarService;
        private readonly SelectCarResponseProcessor _processor;

        public SelectCarResponseProcessorTests()
        {
            _mockCarService = new Mock<ICarService>();
            _processor = new SelectCarResponseProcessor(_mockCarService.Object);
        }

        [Fact]
        public async Task ProcessResponseAsync_WithValidCarId_CallsUpdateCurrentCar()
        {
            // Arrange
            var carId = 5;
            var response = new SelectCarResponse
            {
                Car = carId
            };

            // Act
            await _processor.ProcessResponseAsync(response);

            // Assert
            _mockCarService.Verify(x => x.UpdateCurrentCar(carId), Times.Once);
        }

        [Fact]
        public async Task ProcessResponseAsync_WithZeroCarId_CallsUpdateCurrentCar()
        {
            // Arrange
            var carId = 0;
            var response = new SelectCarResponse
            {
                Car = carId
            };

            // Act
            await _processor.ProcessResponseAsync(response);

            // Assert
            _mockCarService.Verify(x => x.UpdateCurrentCar(carId), Times.Once);
        }

        [Fact]
        public async Task ProcessResponseAsync_WithNegativeCarId_CallsUpdateCurrentCar()
        {
            // Arrange
            var carId = -1;
            var response = new SelectCarResponse
            {
                Car = carId
            };

            // Act
            await _processor.ProcessResponseAsync(response);

            // Assert
            _mockCarService.Verify(x => x.UpdateCurrentCar(carId), Times.Once);
        }

        [Fact]
        public async Task ProcessResponseAsync_CompletesSuccessfully()
        {
            // Arrange
            var response = new SelectCarResponse
            {
                Car = 1
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
            var response = new SelectCarResponse
            {
                Car = 1
            };

            _mockCarService
                .Setup(x => x.UpdateCurrentCar(It.IsAny<int>()))
                .Throws(expectedException);

            // Act & Assert
            var exception = await Assert.ThrowsAsync<InvalidOperationException>(
                () => _processor.ProcessResponseAsync(response));
            Assert.Same(expectedException, exception);
        }

        [Fact]
        public async Task ProcessResponseAsync_CalledMultipleTimes_UpdatesCarServiceEachTime()
        {
            // Arrange
            var response1 = new SelectCarResponse { Car = 1 };
            var response2 = new SelectCarResponse { Car = 2 };
            var response3 = new SelectCarResponse { Car = 3 };

            // Act
            await _processor.ProcessResponseAsync(response1);
            await _processor.ProcessResponseAsync(response2);
            await _processor.ProcessResponseAsync(response3);

            // Assert
            _mockCarService.Verify(x => x.UpdateCurrentCar(1), Times.Once);
            _mockCarService.Verify(x => x.UpdateCurrentCar(2), Times.Once);
            _mockCarService.Verify(x => x.UpdateCurrentCar(3), Times.Once);
            _mockCarService.Verify(x => x.UpdateCurrentCar(It.IsAny<int>()), Times.Exactly(3));
        }
    }
}