using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;

namespace RLIRL.Business.Services
{
    public class CarService(IClientCommandQueue clientCommandQueue) : ICarService
    {
        public IEnumerable<int> FreeCars { get; set; } = [];
        public int? CurrentCar { get; set; }

        public event EventHandler<IEnumerable<int>>? FreeCarsChanged;

        public event EventHandler<int?>? CurrentCarChanged;

        public void UpdateFreeCars(IEnumerable<int> freeCars)
        {
            if (FreeCars != freeCars)
            {
                FreeCars = freeCars;
                FreeCarsChanged?.Invoke(this, freeCars);
            }
        }

        public void UpdateCurrentCar(int? currentCar)
        {
            if (CurrentCar != currentCar)
            {
                CurrentCar = currentCar;
                CurrentCarChanged?.Invoke(this, currentCar);
            }
        }

        public void SelectCar(int carId)
        {
            // Request to select a car
            var selectCarCommand = new SelectCarCommand()
            {
                Car = carId
            };
            clientCommandQueue.EnqueueCommand(selectCarCommand);
        }

        public void ReleaseCar()
        {
            // If no car is currently selected, do nothing
            if (CurrentCar == null) return;

            // Request to release the current car
            var releaseCarCommand = new FreeCarCommand()
            {
                Car = CurrentCar.Value
            };
            clientCommandQueue.EnqueueCommand(releaseCarCommand);
        }
    }
}
