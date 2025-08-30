using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class StartGameResponseProcessor : ServerResponseProcessorBase<StartGameResponse>
    {
        public override Task ProcessResponseAsync(StartGameResponse response)
        {
            throw new NotImplementedException();
        }
    }
}