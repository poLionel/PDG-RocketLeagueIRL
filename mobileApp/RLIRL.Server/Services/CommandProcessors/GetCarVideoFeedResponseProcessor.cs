using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class GetCarVideoFeedResponseProcessor : ServerResponseProcessorBase<GetCarVideoFeedResponse>
    {
        public override Task ProcessResponseAsync(GetCarVideoFeedResponse response)
        {
            throw new NotImplementedException();
        }
    }
}