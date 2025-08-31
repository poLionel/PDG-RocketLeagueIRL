using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;

namespace RLIRL.Business.Services
{
    internal class CarControlService(IClientCommandQueue commandQueue)
    {
        public Directions direction;

        public bool boost;

        public void SetBoot(bool boost)
        {
            this.boost = boost;
            SendUpdateCommand();
        }

        public void SetDirection(Directions direction)
        {
            this.direction = direction;
            SendUpdateCommand();
        }

        private void SendUpdateCommand()
        {
            var command = new MoveCarCommand()
            {
                Direction = direction,
                Boost = boost
            };

            commandQueue.EnqueueCommand(command);
        }
    }
}
