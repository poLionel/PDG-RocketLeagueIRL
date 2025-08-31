using RLIRL.Server.Abstractions.Abstractions;

namespace RLIRL.Server.Abstractions
{
    internal abstract class ServerCommandProcessorBase<T> : IServerCommandProcessor<T> where T : IServerCommand
    {
        public  Task ProcessCommandAsync(object command)
        {
            // Check if the command is of the expected type
            if (command is not T typedCommand)
                throw new InvalidOperationException($"Invalid command type. Expected {typeof(T).Name}, but received {command.GetType().Name}");

            return ProcessCommandAsync(typedCommand);
        }

        public abstract Task ProcessCommandAsync(T command);
    }
}
