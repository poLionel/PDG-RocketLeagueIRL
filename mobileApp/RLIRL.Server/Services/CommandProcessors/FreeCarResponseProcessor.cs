using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class FreeCarResponseProcessor(ICarService carService) : ServerResponseProcessorBase<FreeCarResponse>
    {
        public override Task ProcessResponseAsync(FreeCarResponse response)
        {
            // Release the current car if it matches our car
            if (carService.CurrentCar != response.Car)
            {
                carService.UpdateCurrentCar(null);
            }

            return Task.CompletedTask;
        }
    }
}