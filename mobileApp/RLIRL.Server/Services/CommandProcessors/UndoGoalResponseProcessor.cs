using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerResponses;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class UndoGoalResponseProcessor : ServerResponseProcessorBase<UndoGoalResponse>
    {
        public override Task ProcessResponseAsync(UndoGoalResponse response)
        {
            // Ignore
            return Task.CompletedTask;
        }
    }
}
