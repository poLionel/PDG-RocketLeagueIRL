using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class GetAccessibleCarFeedsResponseProcessor : ServerResponseProcessorBase<GetAccessibleCarFeedsResponse>
    {
        public override Task ProcessResponseAsync(GetAccessibleCarFeedsResponse response)
        {
            throw new NotImplementedException();
        }
    }
}