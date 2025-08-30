namespace RLIRL.Server.Abstractions.Abstractions
{
    public interface IServerResponseProcessor
    {
        /// <summary>
        /// Processes a command from the server
        /// </summary>
        /// <param name="command">Command to process</param>
        /// <returns>A task representing the asynchronous operation</returns>
        Task ProcessCommandAsync(object command);
    }

    public interface IServerResponseProcessor<T> : IServerResponseProcessor where T : IServerResponse
    {
        /// <summary>
        /// Processes a command from the server
        /// </summary>
        /// <param name="command">Command to process</param>
        /// <returns>A task representing the asynchronous operation</returns>
        Task ProcessCommandAsync(T command);
    }
}
