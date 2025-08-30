using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class GetCarStatusResponseProcessor : ServerResponseProcessorBase<GetCarStatusResponse>
    {
        public override Task ProcessCommandAsync(GetCarStatusResponse command)
        {
            throw new NotImplementedException();
        }
    }
}