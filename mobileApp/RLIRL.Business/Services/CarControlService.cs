using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;

namespace RLIRL.Business.Services
{
    /// <summary>
    /// Implementation of the <see cref="ICarControlService"/> interface.
    /// </summary>
    /// <param name="commandQueue">The command queue used to send car control commands to the server.</param>
    public class CarControlService(IClientCommandQueue commandQueue) : ICarControlService
    {

        #region Methods

        /// <inheritdoc />
        public void SetBoost(bool boost)
        {
            _boost = boost;
            SendUpdateCommand();
        }

        /// <inheritdoc />
        public void SetDirection(Directions direction)
        {
            _direction = direction;
            SendUpdateCommand();
        }

        /// <inheritdoc />
        public void SetSteeringValue(int steeringValue)
        {
            _steeringValue = steeringValue;
            SendUpdateCommand();
        }

        /// <summary>
        /// Creates a new move command with the current car state and enqueues it.
        /// </summary>
        private void SendUpdateCommand()
        {
            var command = new MoveCarCommand()
            {
                Direction = _direction,
                Boost = _boost,
                SteeringValue = _steeringValue
            };

            commandQueue.EnqueueCommand(command);
        }

        #endregion

        #region Private fields

        /// <summary>
        /// Represents the direction of the car.
        /// </summary>
        private Directions _direction;

        /// <summary>
        /// Indicates whether the boost is active.
        /// </summary>
        private bool _boost;

        /// <summary>
        /// Represents the steering value.
        /// </summary>
        private int _steeringValue;

        #endregion
    }
}
