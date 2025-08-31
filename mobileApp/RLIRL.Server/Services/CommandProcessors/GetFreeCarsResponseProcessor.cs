using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class GetFreeCarsResponseProcessor : ServerResponseProcessorBase<GetFreeCarsResponse>
    {
        public override Task ProcessResponseAsync(GetFreeCarsResponse response)
        {
            throw new NotImplementedException();
        }
    }
}