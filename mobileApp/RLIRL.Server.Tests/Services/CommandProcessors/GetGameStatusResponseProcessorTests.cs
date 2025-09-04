using AutoMapper;
using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions.ServerCommands;
using RLIRL.Server.Services.CommandProcessors;
using Moq;
using Xunit;

namespace RLIRL.Server.Tests.Services.CommandProcessors
{
    public class GetGameStatusResponseProcessorTests
    {
        private readonly Mock<IGameService> _mockGameService;
        private readonly Mock<IMapper> _mockMapper;
        private readonly GetGameStatusResponseProcessor _processor;

        public GetGameStatusResponseProcessorTests()
        {
            _mockGameService = new Mock<IGameService>();
            _mockMapper = new Mock<IMapper>();
            _processor = new GetGameStatusResponseProcessor(_mockGameService.Object, _mockMapper.Object);
        }

        [Fact]
        public async Task ProcessResponseAsync_WithValidResponse_MapsAndUpdatesGameStatus()
        {
            // Arrange
            var response = new GetGameStatusResponse
            {
                // Add any properties that the response should have
            };
            var mappedGameStatus = new GameStatus();

            _mockMapper
                .Setup(x => x.Map<GameStatus>(response))
                .Returns(mappedGameStatus);

            // Act
            await _processor.ProcessResponseAsync(response);

            // Assert
            _mockMapper.Verify(x => x.Map<GameStatus>(response), Times.Once);
            _mockGameService.Verify(x => x.UpdateGameStatus(mappedGameStatus), Times.Once);
        }

        [Fact]
        public async Task ProcessResponseAsync_CompletesSuccessfully()
        {
            // Arrange
            var response = new GetGameStatusResponse();
            var mappedGameStatus = new GameStatus();

            _mockMapper
                .Setup(x => x.Map<GameStatus>(It.IsAny<GetGameStatusResponse>()))
                .Returns(mappedGameStatus);

            // Act
            var task = _processor.ProcessResponseAsync(response);

            // Assert
            Assert.True(task.IsCompletedSuccessfully);
            await task; // Should not throw
        }

        [Fact]
        public async Task ProcessResponseAsync_WhenMapperThrows_PropagatesException()
        {
            // Arrange
            var expectedException = new AutoMapperMappingException("Mapping failed");
            var response = new GetGameStatusResponse();

            _mockMapper
                .Setup(x => x.Map<GameStatus>(It.IsAny<GetGameStatusResponse>()))
                .Throws(expectedException);

            // Act & Assert
            var exception = await Assert.ThrowsAsync<AutoMapperMappingException>(
                () => _processor.ProcessResponseAsync(response));
            Assert.Same(expectedException, exception);
        }

        [Fact]
        public async Task ProcessResponseAsync_WhenGameServiceThrows_PropagatesException()
        {
            // Arrange
            var expectedException = new InvalidOperationException("Game service error");
            var response = new GetGameStatusResponse();
            var mappedGameStatus = new GameStatus();

            _mockMapper
                .Setup(x => x.Map<GameStatus>(It.IsAny<GetGameStatusResponse>()))
                .Returns(mappedGameStatus);

            _mockGameService
                .Setup(x => x.UpdateGameStatus(It.IsAny<GameStatus>()))
                .Throws(expectedException);

            // Act & Assert
            var exception = await Assert.ThrowsAsync<InvalidOperationException>(
                () => _processor.ProcessResponseAsync(response));
            Assert.Same(expectedException, exception);
        }

        [Fact]
        public async Task ProcessResponseAsync_WithNullResponse_CallsMapperAndGameService()
        {
            // Arrange
            GetGameStatusResponse response = null!;
            var mappedGameStatus = new GameStatus();

            _mockMapper
                .Setup(x => x.Map<GameStatus>(response))
                .Returns(mappedGameStatus);

            // Act
            await _processor.ProcessResponseAsync(response);

            // Assert
            _mockMapper.Verify(x => x.Map<GameStatus>(response), Times.Once);
            _mockGameService.Verify(x => x.UpdateGameStatus(mappedGameStatus), Times.Once);
        }

        [Fact]
        public async Task ProcessResponseAsync_WithNullMappedGameStatus_CallsGameServiceWithNull()
        {
            // Arrange
            var response = new GetGameStatusResponse();
            GameStatus mappedGameStatus = null!;

            _mockMapper
                .Setup(x => x.Map<GameStatus>(It.IsAny<GetGameStatusResponse>()))
                .Returns(mappedGameStatus);

            // Act
            await _processor.ProcessResponseAsync(response);

            // Assert
            _mockMapper.Verify(x => x.Map<GameStatus>(response), Times.Once);
            _mockGameService.Verify(x => x.UpdateGameStatus(mappedGameStatus), Times.Once);
        }
    }
}