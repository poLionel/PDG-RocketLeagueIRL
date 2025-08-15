using RLIRL.Server.Abstractions;
using RLIRL.Server.Services.ServerCommands;

namespace RLIRL.Server.Services.ServerCommandsProcessors
{
    internal class GameStatusCommandProcessor : ServerCommandProcessorBase<GameStatusServerCommand>
    {
        public override Task ProcessCommandAsync(GameStatusServerCommand command)
        {
            throw new NotImplementedException();
        }
    }
}
