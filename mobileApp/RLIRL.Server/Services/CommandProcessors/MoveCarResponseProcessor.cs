using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class MoveCarResponseProcessor : ServerResponseProcessorBase<MoveCarResponse>
    {
        public override Task ProcessResponseAsync(MoveCarResponse response)
        {
            throw new NotImplementedException();
        }
    }
}