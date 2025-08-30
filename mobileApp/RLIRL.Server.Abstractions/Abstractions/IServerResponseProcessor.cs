namespace RLIRL.Server.Abstractions.Abstractions
{
    public interface IServerResponseProcessor
    {
        /// <summary>
        /// Processes a response from the server
        /// </summary>
        /// <param name="response">Response to process</param>
        /// <returns>A task representing the asynchronous operation</returns>
        Task ProcessResponseAsync(object response);
    }

    public interface IServerResponseProcessor<T> : IServerResponseProcessor where T : IServerResponse
    {
        /// <summary>
        /// Processes a response from the server
        /// </summary>
        /// <param name="response">Response to process</param>
        /// <returns>A task representing the asynchronous operation</returns>
        Task ProcessResponseAsync(T response);
    }
}
