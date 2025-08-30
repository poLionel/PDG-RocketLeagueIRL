using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class GoalScoredResponseProcessor : ServerResponseProcessorBase<GoalScoredResponse>
    {
        public override Task ProcessResponseAsync(GoalScoredResponse response)
        {
            throw new NotImplementedException();
        }
    }
}