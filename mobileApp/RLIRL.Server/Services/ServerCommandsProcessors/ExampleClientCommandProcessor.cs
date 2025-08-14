using RLIRL.Server.Abstractions;
using RLIRL.Server.Services.Server.ServerCommands;

namespace RLIRL.Server.Services.Server.CommandProcessors
{
    internal class ExampleClientCommandProcessor : ServerCommandProcessorBase<ExampleServerCommand>
    {
        public override Task ProcessCommandAsync(ExampleServerCommand command)
        {
            throw new NotImplementedException();
        }
    }
}
