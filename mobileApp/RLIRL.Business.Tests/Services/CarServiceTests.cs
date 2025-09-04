using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Services;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;
using Moq;
using Xunit;

namespace RLIRL.Business.Tests.Services
{
    public class CarServiceTests
    {
        private readonly Mock<IClientCommandQueue> _mockCommandQueue;
        private readonly CarService _service;

        public CarServiceTests()
        {
            _mockCommandQueue = new Mock<IClientCommandQueue>();
            _service = new CarService(_mockCommandQueue.Object);
        }

        [Fact]
        public void Constructor_SendsGetFreeCarsCommand()
        {
            // Assert - Constructor should send initial refresh command
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<GetFreeCarsCommand>()), 
                Times.Once);
        }

        [Fact]
        public void FreeCars_InitiallyEmpty()
        {
            // Assert
            Assert.Empty(_service.FreeCars);
        }

        [Fact]
        public void CurrentCar_InitiallyNull()
        {
            // Assert
            Assert.Null(_service.CurrentCar);
        }

        [Fact]
        public void UpdateFreeCars_WithNewFreeCars_UpdatesProperty()
        {
            // Arrange
            var freeCars = new[] { 1, 2, 3 };

            // Act
            _service.UpdateFreeCars(freeCars);

            // Assert
            Assert.Equal(freeCars, _service.FreeCars);
        }

        [Fact]
        public void UpdateFreeCars_WithNewFreeCars_RaisesEvent()
        {
            // Arrange
            var freeCars = new[] { 1, 2, 3 };
            IEnumerable<int>? eventArgs = null;
            _service.FreeCarsChanged += (sender, args) => eventArgs = args;

            // Act
            _service.UpdateFreeCars(freeCars);

            // Assert
            Assert.Equal(freeCars, eventArgs);
        }

        [Fact]
        public void UpdateFreeCars_WithSameFreeCars_DoesNotRaiseEvent()
        {
            // Arrange
            var freeCars = new[] { 1, 2, 3 };
            _service.UpdateFreeCars(freeCars);
            
            var eventRaised = false;
            _service.FreeCarsChanged += (sender, args) => eventRaised = true;

            // Act
            _service.UpdateFreeCars(freeCars);

            // Assert
            Assert.False(eventRaised);
        }

        [Fact]
        public void UpdateCurrentCar_WithNewCar_UpdatesProperty()
        {
            // Arrange
            var carId = 5;

            // Act
            _service.UpdateCurrentCar(carId);

            // Assert
            Assert.Equal(carId, _service.CurrentCar);
        }

        [Fact]
        public void UpdateCurrentCar_WithNewCar_RaisesEvent()
        {
            // Arrange
            var carId = 5;
            int? eventArgs = null;
            _service.CurrentCarChanged += (sender, args) => eventArgs = args;

            // Act
            _service.UpdateCurrentCar(carId);

            // Assert
            Assert.Equal(carId, eventArgs);
        }

        [Fact]
        public void UpdateCurrentCar_WithSameCar_DoesNotRaiseEvent()
        {
            // Arrange
            var carId = 5;
            _service.UpdateCurrentCar(carId);
            
            var eventRaised = false;
            _service.CurrentCarChanged += (sender, args) => eventRaised = true;

            // Act
            _service.UpdateCurrentCar(carId);

            // Assert
            Assert.False(eventRaised);
        }

        [Fact]
        public void UpdateCurrentCar_WithNull_UpdatesPropertyToNull()
        {
            // Arrange
            _service.UpdateCurrentCar(5); // Set to non-null first

            // Act
            _service.UpdateCurrentCar(null);

            // Assert
            Assert.Null(_service.CurrentCar);
        }

        [Fact]
        public void Refresh_EnqueuesGetFreeCarsCommand()
        {
            // Act
            _service.Refresh();

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<GetFreeCarsCommand>()), 
                Times.AtLeast(2)); // Once in constructor, once in Refresh
        }

        [Fact]
        public void SelectCar_EnqueuesSelectCarCommand()
        {
            // Arrange
            var carId = 3;

            // Act
            _service.SelectCar(carId);

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.Is<SelectCarCommand>(cmd => cmd.Car == carId)), 
                Times.Once);
        }

        [Fact]
        public void ReleaseCar_WhenCurrentCarIsNull_DoesNotEnqueueCommand()
        {
            // Arrange
            _service.UpdateCurrentCar(null);

            // Act
            _service.ReleaseCar();

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<FreeCarCommand>()), 
                Times.Never);
        }

        [Fact]
        public void ReleaseCar_WhenCurrentCarIsSet_EnqueuesFreeCarCommand()
        {
            // Arrange
            var carId = 4;
            _service.UpdateCurrentCar(carId);

            // Act
            _service.ReleaseCar();

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.Is<FreeCarCommand>(cmd => cmd.Car == carId)), 
                Times.Once);
        }

        [Fact]
        public void UpdateFreeCars_WithEmptyCollection_UpdatesProperty()
        {
            // Arrange
            var freeCars = Array.Empty<int>();

            // Act
            _service.UpdateFreeCars(freeCars);

            // Assert
            Assert.Empty(_service.FreeCars);
        }

        [Fact]
        public void FreeCarsChanged_EventHandlerSignature_IsCorrect()
        {
            // Arrange
            var handlerCalled = false;
            EventHandler<IEnumerable<int>>? handler = (sender, args) =>
            {
                Assert.Same(_service, sender);
                Assert.NotNull(args);
                handlerCalled = true;
            };

            _service.FreeCarsChanged += handler;

            // Act
            _service.UpdateFreeCars(new[] { 1 });

            // Assert
            Assert.True(handlerCalled);
        }

        [Fact]
        public void CurrentCarChanged_EventHandlerSignature_IsCorrect()
        {
            // Arrange
            var handlerCalled = false;
            EventHandler<int?>? handler = (sender, args) =>
            {
                Assert.Same(_service, sender);
                handlerCalled = true;
            };

            _service.CurrentCarChanged += handler;

            // Act
            _service.UpdateCurrentCar(1);

            // Assert
            Assert.True(handlerCalled);
        }
    }
}