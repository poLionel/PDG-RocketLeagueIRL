using RLIRL.Server.Abstractions.ClientCommands;

namespace RLIRL.Business.Abstractions.Abstractions
{
    /// <summary>
    /// Provides services to control a car by updating its state and enqueuing corresponding commands
    /// into the client command queue.
    /// </summary>
    public interface ICarControlService
    {
        /// <summary>
        /// Sets the current boost and queues an update command.
        /// </summary>
        /// <param name="boost">Whether the boost is active.</param>
        public void SetBoost(bool boost);

        /// <summary>
        /// Sets the current direction (forward, backward, stopped) of the car and queues an update command.
        /// </summary>
        /// <param name="direction">The current driving direction.</param>
        public void SetDirection(Directions direction);

        /// <summary>
        /// Sets the current steering value of the car (-100 : full left, 100 : full right, 0 : straight)
        /// and queues an update command.
        /// </summary>
        /// <param name="steeringValue">Steering value.</param>
        public void SetSteeringValue(int steeringValue);
    }
}
