using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class GetFreeCarsResponseProcessor(ICarService carService) : ServerResponseProcessorBase<GetFreeCarsResponse>
    {
        public override Task ProcessResponseAsync(GetFreeCarsResponse response)
        {
            carService.UpdateFreeCars(response.FreeCars);
            return Task.CompletedTask;
        }
    }
}