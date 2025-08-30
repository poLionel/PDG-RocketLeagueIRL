using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class StopGameResponseProcessor : ServerResponseProcessorBase<StopGameResponse>
    {
        public override Task ProcessCommandAsync(StopGameResponse command)
        {
            throw new NotImplementedException();
        }
    }
}