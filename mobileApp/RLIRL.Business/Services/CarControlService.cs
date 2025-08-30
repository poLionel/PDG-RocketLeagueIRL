using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;

namespace RLIRL.Business.Services
{
    internal class CarControlService(IClientCommandQueue commandQueue)
    {
        public Direction direction = Direction.Forward;
        public int carId;
        public int steering;
        public bool boost;

        public void SetBoot(bool boost)
        {
            this.boost = boost;
            SendUpdateCommand();
        }

        public void SetDirection(Direction direction)
        {
            this.direction = direction;
            SendUpdateCommand();
        }

        public void SetSteering(int steering)
        {
            this.steering = steering;
            SendUpdateCommand();
        }

        public void SetCar(int carId)
        {
            this.carId = carId;
        }

        private void SendUpdateCommand()
        {
            var command = new MoveCarCommand()
            {
                Car = carId,
                Direction = direction,
                Steering = steering,
                Boost = boost ? "true" : "false"
            };

            commandQueue.EnqueueCommand(command);
        }
    }
}
