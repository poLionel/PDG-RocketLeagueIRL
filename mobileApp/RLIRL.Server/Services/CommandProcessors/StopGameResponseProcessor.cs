using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class StopGameResponseProcessor : ServerResponseProcessorBase<StopGameResponse>
    {
        public override Task ProcessResponseAsync(StopGameResponse response)
        {
            throw new NotImplementedException();
        }
    }
}