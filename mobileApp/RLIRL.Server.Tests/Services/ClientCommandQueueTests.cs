using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;
using System.Threading.Channels;
using Xunit;

namespace RLIRL.Server.Tests.Services
{
    public class ClientCommandQueueTests
    {
        private readonly ClientCommandQueue _queue;

        public ClientCommandQueueTests()
        {
            _queue = new ClientCommandQueue();
        }

        [Fact]
        public void EnqueueCommand_WithValidCommand_DoesNotThrow()
        {
            // Arrange
            var command = new GetFreeCarsCommand();

            // Act & Assert
            var exception = Record.Exception(() => _queue.EnqueueCommand(command));
            Assert.Null(exception);
        }

        [Fact]
        public async Task DequeueCommandAsync_WithEnqueuedCommand_ReturnsCorrectCommand()
        {
            // Arrange
            var command = new GetFreeCarsCommand();
            _queue.EnqueueCommand(command);

            // Act
            var result = await _queue.DequeueCommandAsync();

            // Assert
            Assert.Same(command, result);
        }

        [Fact]
        public async Task DequeueCommandAsync_WithMultipleCommands_ReturnsInFifoOrder()
        {
            // Arrange
            var command1 = new GetFreeCarsCommand();
            var command2 = new SelectCarCommand { Car = 1 };
            var command3 = new GetGameStatusCommand();

            _queue.EnqueueCommand(command1);
            _queue.EnqueueCommand(command2);
            _queue.EnqueueCommand(command3);

            // Act
            var result1 = await _queue.DequeueCommandAsync();
            var result2 = await _queue.DequeueCommandAsync();
            var result3 = await _queue.DequeueCommandAsync();

            // Assert
            Assert.Same(command1, result1);
            Assert.Same(command2, result2);
            Assert.Same(command3, result3);
        }

        [Fact]
        public async Task DequeueCommandAsync_WithCancellation_ThrowsOperationCanceledException()
        {
            // Arrange
            using var cts = new CancellationTokenSource(TimeSpan.FromMilliseconds(100));

            // Act & Assert
            await Assert.ThrowsAsync<OperationCanceledException>(
                () => _queue.DequeueCommandAsync(cts.Token));
        }

        [Fact]
        public async Task EnqueueAndDequeue_WithConcurrentOperations_WorksCorrectly()
        {
            // Arrange
            const int commandCount = 100;
            var commands = Enumerable.Range(0, commandCount)
                .Select(i => new SelectCarCommand { Car = i })
                .Cast<IClientCommand>()
                .ToList();

            // Act - Enqueue commands concurrently
            var enqueueTasks = commands.Select(cmd => Task.Run(() => _queue.EnqueueCommand(cmd)));
            await Task.WhenAll(enqueueTasks);

            // Dequeue all commands
            var dequeuedCommands = new List<IClientCommand>();
            for (int i = 0; i < commandCount; i++)
            {
                var command = await _queue.DequeueCommandAsync();
                dequeuedCommands.Add(command);
            }

            // Assert
            Assert.Equal(commandCount, dequeuedCommands.Count);
            
            // All commands should be present (order may vary due to concurrency)
            var originalCarIds = commands.Cast<SelectCarCommand>().Select(c => c.Car).OrderBy(x => x);
            var dequeuedCarIds = dequeuedCommands.Cast<SelectCarCommand>().Select(c => c.Car).OrderBy(x => x);
            Assert.Equal(originalCarIds, dequeuedCarIds);
        }

        [Fact]
        public void EnqueueCommand_WithNullCommand_DoesNotThrow()
        {
            // Arrange
            IClientCommand command = null!;

            // Act & Assert
            var exception = Record.Exception(() => _queue.EnqueueCommand(command));
            Assert.Null(exception);
        }
    }
}