using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class SelectCarResponseProcessor : ServerResponseProcessorBase<SelectCarResponse>
    {
        public override Task ProcessCommandAsync(SelectCarResponse command)
        {
            throw new NotImplementedException();
        }
    }
}