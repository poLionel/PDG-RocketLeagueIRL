using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class StartGameResponseProcessor : ServerResponseProcessorBase<StartGameResponse>
    {
        public override Task ProcessCommandAsync(StartGameResponse command)
        {
            throw new NotImplementedException();
        }
    }
}