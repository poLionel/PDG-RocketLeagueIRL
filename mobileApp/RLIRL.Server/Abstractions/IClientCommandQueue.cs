namespace RLIRL.Server.Abstractions.Server
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
        /// Dequeues a command from the queue for processing by the server
        /// </summary>
        /// <returns>Command to process, or null if no commands are available</returns>
        IClientCommand? DequeueCommand();
    }
}
