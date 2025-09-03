using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class SelectCarResponseProcessor(ICarService carService) : ServerResponseProcessorBase<SelectCarResponse>
    {
        public override Task ProcessResponseAsync(SelectCarResponse response)
        {
            // Update the current car in the car service
            carService.UpdateCurrentCar(response.Car);
            return Task.CompletedTask;
        }
    }
}