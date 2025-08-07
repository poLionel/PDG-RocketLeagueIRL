using RLIRL.Services.Abstractions.Server;
using RLIRL.Services.Services.Server.ServerCommands;

namespace RLIRL.Services.Services.Server.CommandProcessors
{
    internal class ExampleClientCommandProcessor : IServerCommandProcessor<ExampleServerCommand>
    {
        public Task ProcessCommandAsync(ExampleServerCommand command)
        {
            throw new NotImplementedException();
        }
    }
}
