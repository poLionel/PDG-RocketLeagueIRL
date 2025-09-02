using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;

namespace RLIRL.Business.Services
{
    /// <summary>
    /// Implementation of the <see cref="ICarControlService"/> interface.
    /// </summary>
    /// <param name="commandQueue">The command queue used to send car control commands to the server.</param>
    public class CarControlService(IClientCommandQueue commandQueue, ICarService carService) : ICarControlService
    {
        #region Private fields

        /// <summary>
        /// Represents the ID of the car being controlled.
        /// </summary>
        private int _carId;

        /// <summary>
        /// Represents the direction of the car.
        /// </summary>
        private Direction _direction;

        /// <summary>
        /// Indicates whether the boost is active.
        /// </summary>
        private bool _boost;

        /// <summary>
        /// Represents the steering value.
        /// </summary>
        private int _steering;

        #endregion

        #region Methods

        public void SetBoost(bool boost)
        {
            _boost = boost;
            SendUpdateCommand();
        }

        public void SetDirection(Direction direction)
        {
            _direction = direction;
            SendUpdateCommand();
        }

        public void SetSteering(int steering)
        {
            _steering = steering;
            SendUpdateCommand();
        }

        /// <summary>
        /// Creates a new move command with the current car state and enqueues it.
        /// </summary>
        private void SendUpdateCommand()
        {
            // If there is no current car, do not send any command
            if (carService.CurrentCar == null) return;

            var command = new MoveCarCommand()
            {
                Direction = _direction,
                Boost = _boost,
                Steering = _steering,
                Car = carService.CurrentCar.Value
            };

            commandQueue.EnqueueCommand(command);
        }

        #endregion
    }
}
