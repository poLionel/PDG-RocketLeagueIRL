using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Services;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;
using RLIRL.Server.Abstractions.ServerResponses;
using Moq;
using Xunit;

namespace RLIRL.Business.Tests.Services
{
    public class CameraFeedServiceTests
    {
        private readonly Mock<IClientCommandQueue> _mockCommandQueue;
        private readonly CameraFeedService _service;

        public CameraFeedServiceTests()
        {
            _mockCommandQueue = new Mock<IClientCommandQueue>();
            _service = new CameraFeedService(_mockCommandQueue.Object);
        }

        [Fact]
        public void Constructor_SendsGetAccessibleCarFeedsCommand()
        {
            // Assert - The constructor should not enqueue any commands
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<GetAccessibleCarFeedsCommand>()), 
                Times.Never);
        }

        [Fact]
        public void CameraFeeds_InitiallyEmpty()
        {
            // Assert
            Assert.Empty(_service.CameraFeeds);
        }

        [Fact]
        public void UpdateAvailableFeeds_WithNewFeeds_UpdatesProperty()
        {
            // Arrange
            var feeds = new[]
            {
                new CameraFeed { CarId = 1, Url = "http://example.com/car1" },
                new CameraFeed { CarId = 2, Url = "http://example.com/car2" }
            };

            // Act
            _service.UpdateAvailableFeeds(feeds);

            // Assert
            Assert.Equal(feeds, _service.CameraFeeds);
        }

        [Fact]
        public void UpdateAvailableFeeds_WithNewFeeds_RaisesEvent()
        {
            // Arrange
            var feeds = new[]
            {
                new CameraFeed { CarId = 3, Url = "http://example.com/car3" }
            };
            IEnumerable<CameraFeed>? eventArgs = null;
            _service.CameraFeedsChanged += (sender, args) => eventArgs = args;

            // Act
            _service.UpdateAvailableFeeds(feeds);

            // Assert
            Assert.Equal(feeds, eventArgs);
        }

        [Fact]
        public void UpdateAvailableFeeds_WithSameFeeds_DoesNotRaiseEvent()
        {
            // Arrange
            var feeds = new[]
            {
                new CameraFeed { CarId = 4, Url = "http://example.com/car4" }
            };
            _service.UpdateAvailableFeeds(feeds);
            
            var eventRaised = false;
            _service.CameraFeedsChanged += (sender, args) => eventRaised = true;

            // Act
            _service.UpdateAvailableFeeds(feeds);

            // Assert
            Assert.False(eventRaised);
        }

        [Fact]
        public void UpdateAvailableFeeds_WithEmptyCollection_UpdatesProperty()
        {
            // Arrange
            var feeds = Array.Empty<CameraFeed>();

            // Act
            _service.UpdateAvailableFeeds(feeds);

            // Assert
            Assert.Empty(_service.CameraFeeds);
        }

        [Fact]
        public void UpdateAvailableFeeds_WithNull_UpdatesPropertyToNull()
        {
            // Arrange
            var feeds = new[] { new CameraFeed { CarId = 5, Url = "http://example.com/car5" } };
            _service.UpdateAvailableFeeds(feeds); // Set to non-null first

            // Act
            _service.UpdateAvailableFeeds(null!);

            // Assert
            Assert.Null(_service.CameraFeeds);
        }

        [Fact]
        public void Refresh_EnqueuesGetAccessibleCarFeedsCommand()
        {
            // Act
            _service.Refresh();

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<GetAccessibleCarFeedsCommand>()), 
                Times.AtLeast(1));
        }

        [Fact]
        public void CameraFeedsChanged_EventHandlerSignature_IsCorrect()
        {
            // Arrange
            var handlerCalled = false;
            var feeds = new[] { new CameraFeed { CarId = 6, Url = "http://example.com/car6" } };
            
            EventHandler<IEnumerable<CameraFeed>>? handler = (sender, args) =>
            {
                Assert.Same(_service, sender);
                Assert.Equal(feeds, args);
                handlerCalled = true;
            };

            _service.CameraFeedsChanged += handler;

            // Act
            _service.UpdateAvailableFeeds(feeds);

            // Assert
            Assert.True(handlerCalled);
        }

        [Fact]
        public void UpdateAvailableFeeds_WithDifferentFeedCollections_UpdatesCorrectly()
        {
            // Arrange
            var feeds1 = new[] { new CameraFeed { CarId = 1, Url = "http://example.com/car1" } };
            var feeds2 = new[] 
            { 
                new CameraFeed { CarId = 2, Url = "http://example.com/car2" },
                new CameraFeed { CarId = 3, Url = "http://example.com/car3" }
            };

            // Act & Assert
            _service.UpdateAvailableFeeds(feeds1);
            Assert.Equal(feeds1, _service.CameraFeeds);

            _service.UpdateAvailableFeeds(feeds2);
            Assert.Equal(feeds2, _service.CameraFeeds);
        }

        [Fact]
        public void MultipleRefreshCalls_EnqueueMultipleCommands()
        {
            // Act
            _service.Refresh();
            _service.Refresh();
            _service.Refresh();

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<GetAccessibleCarFeedsCommand>()), 
                Times.AtLeast(3));
        }

        [Fact]
        public void UpdateAvailableFeeds_WithCameraFeeds_MaintainsCarIdAndUrl()
        {
            // Arrange
            var feeds = new[]
            {
                new CameraFeed { CarId = 10, Url = "http://192.168.1.100:8080/car10" },
                new CameraFeed { CarId = 11, Url = "http://192.168.1.101:8080/car11" }
            };

            // Act
            _service.UpdateAvailableFeeds(feeds);

            // Assert
            var cameraFeeds = _service.CameraFeeds.ToArray();
            Assert.Equal(2, cameraFeeds.Length);
            Assert.Equal(10, cameraFeeds[0].CarId);
            Assert.Equal("http://192.168.1.100:8080/car10", cameraFeeds[0].Url);
            Assert.Equal(11, cameraFeeds[1].CarId);
            Assert.Equal("http://192.168.1.101:8080/car11", cameraFeeds[1].Url);
        }

        [Fact]
        public void UpdateAvailableFeeds_WithEventUnsubscription_DoesNotCallHandler()
        {
            // Arrange
            var handlerCalled = false;
            EventHandler<IEnumerable<CameraFeed>> handler = (sender, args) => handlerCalled = true;
            
            _service.CameraFeedsChanged += handler;
            _service.CameraFeedsChanged -= handler;

            // Act
            _service.UpdateAvailableFeeds(new[] { new CameraFeed { CarId = 7, Url = "http://example.com/car7" } });

            // Assert
            Assert.False(handlerCalled);
        }
    }
}