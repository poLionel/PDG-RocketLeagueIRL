using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Services;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;
using Moq;
using Xunit;

namespace RLIRL.Business.Tests.Services
{
    public class CarControlServiceTests
    {
        private readonly Mock<IClientCommandQueue> _mockCommandQueue;
        private readonly Mock<ICarService> _mockCarService;
        private readonly CarControlService _service;

        public CarControlServiceTests()
        {
            _mockCommandQueue = new Mock<IClientCommandQueue>();
            _mockCarService = new Mock<ICarService>();
            _service = new CarControlService(_mockCommandQueue.Object, _mockCarService.Object);
        }

        [Fact]
        public void SetBoost_WithTrue_SendsCommandWithBoostEnabled()
        {
            // Arrange
            var carId = 5;
            _mockCarService.Setup(x => x.CurrentCar).Returns(carId);

            // Act
            _service.SetBoost(true);

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.Is<MoveCarCommand>(cmd => 
                    cmd.Car == carId && cmd.Boost == true)), 
                Times.Once);
        }

        [Fact]
        public void SetBoost_WithFalse_SendsCommandWithBoostDisabled()
        {
            // Arrange
            var carId = 3;
            _mockCarService.Setup(x => x.CurrentCar).Returns(carId);

            // Act
            _service.SetBoost(false);

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.Is<MoveCarCommand>(cmd => 
                    cmd.Car == carId && cmd.Boost == false)), 
                Times.Once);
        }

        [Fact]
        public void SetDirection_WithForward_SendsCommandWithCorrectDirection()
        {
            // Arrange
            var carId = 2;
            _mockCarService.Setup(x => x.CurrentCar).Returns(carId);

            // Act
            _service.SetDirection(Direction.Forward);

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.Is<MoveCarCommand>(cmd => 
                    cmd.Car == carId && cmd.Direction == Direction.Forward)), 
                Times.Once);
        }

        [Fact]
        public void SetDirection_WithBackward_SendsCommandWithCorrectDirection()
        {
            // Arrange
            var carId = 7;
            _mockCarService.Setup(x => x.CurrentCar).Returns(carId);

            // Act
            _service.SetDirection(Direction.Backward);

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.Is<MoveCarCommand>(cmd => 
                    cmd.Car == carId && cmd.Direction == Direction.Backward)), 
                Times.Once);
        }

        [Fact]
        public void SetSteering_WithPositiveValue_SendsCommandWithCorrectSteering()
        {
            // Arrange
            var carId = 1;
            var steering = 25;
            _mockCarService.Setup(x => x.CurrentCar).Returns(carId);

            // Act
            _service.SetSteering(steering);

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.Is<MoveCarCommand>(cmd => 
                    cmd.Car == carId && cmd.Steering == steering)), 
                Times.Once);
        }

        [Fact]
        public void SetSteering_WithNegativeValue_SendsCommandWithCorrectSteering()
        {
            // Arrange
            var carId = 4;
            var steering = -15;
            _mockCarService.Setup(x => x.CurrentCar).Returns(carId);

            // Act
            _service.SetSteering(steering);

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.Is<MoveCarCommand>(cmd => 
                    cmd.Car == carId && cmd.Steering == steering)), 
                Times.Once);
        }

        [Fact]
        public void SetSteering_WithZero_SendsCommandWithZeroSteering()
        {
            // Arrange
            var carId = 6;
            _mockCarService.Setup(x => x.CurrentCar).Returns(carId);

            // Act
            _service.SetSteering(0);

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.Is<MoveCarCommand>(cmd => 
                    cmd.Car == carId && cmd.Steering == 0)), 
                Times.Once);
        }

        [Fact]
        public void SetBoost_WhenNoCurrentCar_DoesNotSendCommand()
        {
            // Arrange
            _mockCarService.Setup(x => x.CurrentCar).Returns((int?)null);

            // Act
            _service.SetBoost(true);

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<MoveCarCommand>()), 
                Times.Never);
        }

        [Fact]
        public void SetDirection_WhenNoCurrentCar_DoesNotSendCommand()
        {
            // Arrange
            _mockCarService.Setup(x => x.CurrentCar).Returns((int?)null);

            // Act
            _service.SetDirection(Direction.Forward);

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<MoveCarCommand>()), 
                Times.Never);
        }

        [Fact]
        public void SetSteering_WhenNoCurrentCar_DoesNotSendCommand()
        {
            // Arrange
            _mockCarService.Setup(x => x.CurrentCar).Returns((int?)null);

            // Act
            _service.SetSteering(10);

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<MoveCarCommand>()), 
                Times.Never);
        }

        [Fact]
        public void MultipleSetCalls_SendsMultipleCommands()
        {
            // Arrange
            var carId = 8;
            _mockCarService.Setup(x => x.CurrentCar).Returns(carId);

            // Act
            _service.SetBoost(true);
            _service.SetDirection(Direction.Forward);
            _service.SetSteering(20);

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<MoveCarCommand>()), 
                Times.Exactly(3));
        }

        [Fact]
        public void SetCalls_MaintainLatestState()
        {
            // Arrange
            var carId = 9;
            _mockCarService.Setup(x => x.CurrentCar).Returns(carId);

            // Act - Set multiple values
            _service.SetBoost(true);
            _service.SetDirection(Direction.Forward);
            _service.SetSteering(30);

            // Assert - Last command should have all latest values
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.Is<MoveCarCommand>(cmd => 
                    cmd.Car == carId && 
                    cmd.Boost == true && 
                    cmd.Direction == Direction.Forward && 
                    cmd.Steering == 30)), 
                Times.Once);
        }

        [Fact]
        public void SetCalls_WithChangingCarId_UsesCurrentCarId()
        {
            // Arrange
            var initialCarId = 1;
            var newCarId = 2;
            
            _mockCarService.Setup(x => x.CurrentCar).Returns(initialCarId);
            _service.SetBoost(true);

            // Change the current car
            _mockCarService.Setup(x => x.CurrentCar).Returns(newCarId);

            // Act
            _service.SetDirection(Direction.Backward);

            // Assert - Should use the new car ID
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.Is<MoveCarCommand>(cmd => cmd.Car == newCarId)), 
                Times.Once);
        }

        [Fact]
        public void Constructor_WithValidParameters_DoesNotThrow()
        {
            // Act & Assert
            var exception = Record.Exception(() => new CarControlService(
                _mockCommandQueue.Object, 
                _mockCarService.Object));
            Assert.Null(exception);
        }
    }
}