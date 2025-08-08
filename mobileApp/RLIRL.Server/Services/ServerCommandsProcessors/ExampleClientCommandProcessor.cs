using RLIRL.Server.Abstractions.Server;
using RLIRL.Server.Services.Server.ServerCommands;

namespace RLIRL.Server.Services.Server.CommandProcessors
{
    internal class ExampleClientCommandProcessor : IServerCommandProcessor<ExampleServerCommand>
    {
        public Task ProcessCommandAsync(ExampleServerCommand command)
        {
            throw new NotImplementedException();
        }
    }
}
