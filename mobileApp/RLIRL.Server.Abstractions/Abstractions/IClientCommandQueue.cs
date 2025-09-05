namespace RLIRL.Server.Abstractions.Abstractions
{
    /// <summary>
    /// Interface for a queue that holds commands sent from the client to the server 
    /// </summary>
    public interface IClientCommandQueue
    {
        /// <summary>
        /// Enqueues a command to be processed by the server
        /// </summary>
        /// <param name="command">Command to enqueue</param>
        void EnqueueCommand(IClientCommand command);

        /// <summary>
        /// Wait for a command to be available in the queue and dequeue it
        /// </summary>
        /// <param name="cancellationToken">Cancellation token to cancel the operation</param>
        /// <returns>A command from the queue</returns>
        Task<IClientCommand> DequeueCommandAsync(CancellationToken cancellationToken);
    }
}
