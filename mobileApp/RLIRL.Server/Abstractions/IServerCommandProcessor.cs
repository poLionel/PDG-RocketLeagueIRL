namespace RLIRL.Server.Abstractions.Server
{
    public interface IServerCommandProcessor
    {
        /// <summary>
        /// Processes a command from the server
        /// </summary>
        /// <param name="command">Command to process</param>
        /// <returns>A task representing the asynchronous operation</returns>
        Task ProcessCommandAsync(object command);
    }

    public interface IServerCommandProcessor<T> : IServerCommandProcessor where T : IServerCommand
    {
        /// <summary>
        /// Processes a command from the server
        /// </summary>
        /// <param name="command">Command to process</param>
        /// <returns>A task representing the asynchronous operation</returns>
        Task ProcessCommandAsync(T command);
    }
}
