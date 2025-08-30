using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;

namespace RLIRL.Business.Services
{
    /// <summary>
    /// Provides services to control a car by updating its state and enqueuing corresponding commands
    /// into the client command queue.
    /// </summary>
    /// <param name="commandQueue"></param>
    public class CarControlService(IClientCommandQueue commandQueue)
    {

        #region Methods

        /// <summary>
        /// Sets the current boost and queues an update command.
        /// </summary>
        /// <param name="boost">Wheter the boost is active..</param>
        public void SetBoost(bool boost)
        {
            _boost = boost;
            SendUpdateCommand();
        }

        /// <summary>
        /// Sets the current directions (forward, backward, stopped) of the car and queues an update command.
        /// </summary>
        /// <param name="direction">The current driving direction.</param>
        public void SetDirection(Directions direction)
        {
            _direction = direction;
            SendUpdateCommand();
        }

        /// <summary>
        /// Sets the current steering value of the car (-100 : full left, 100 : full right, 0 : straight)
        /// and queues an udpate command.
        /// </summary>
        /// <param name="x"></param>
        public void SetSteeringValue(int x)
        {
            _steeringValue = x;
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
        /// Direction of the car.
        /// </summary>
        private Directions _direction;

        /// <summary>
        /// True if boost is active.
        /// </summary>
        private bool _boost;

        /// <summary>
        /// True if the car is moving;
        /// </summary>
        private int _steeringValue;

        #endregion
    }
}
