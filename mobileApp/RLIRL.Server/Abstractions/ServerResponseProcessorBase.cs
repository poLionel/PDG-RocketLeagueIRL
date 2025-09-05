using RLIRL.Server.Abstractions.Abstractions;

namespace RLIRL.Server.Abstractions
{
    internal abstract class ServerResponseProcessorBase<T> : IServerResponseProcessor<T> where T : IServerResponse
    {
        public  Task ProcessResponseAsync(object response)
        {
            // Check if the command is of the expected type
            if (response is not T typedCommand)
                throw new InvalidOperationException($"Invalid command type. Expected {typeof(T).Name}, but received {response.GetType().Name}");

            return ProcessResponseAsync(typedCommand);
        }

        public abstract Task ProcessResponseAsync(T response);
    }
}
