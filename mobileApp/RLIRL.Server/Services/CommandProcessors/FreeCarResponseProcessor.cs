using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class FreeCarResponseProcessor : ServerResponseProcessorBase<FreeCarResponse>
    {
        public override Task ProcessCommandAsync(FreeCarResponse command)
        {
            throw new NotImplementedException();
        }
    }
}