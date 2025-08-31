using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Reflection;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace RLIRL.Server.Services
{
    internal class ServerCommandSerializer : IServerCommandSerializer
    {
        public byte[] SerializeCommand(IClientCommand serverCommand)
        {
            // If the command has a CommandNameAttribute, use it as the action property
            var action = serverCommand.GetType().GetCustomAttribute<CommandNameAttribute>()?.Name;
            var jsonNode = JsonSerializer.SerializeToNode(serverCommand) as JsonObject;
            if (jsonNode != null && action != null)
            {
                jsonNode["action"] = action;
            }

            // Encode the command
            var jsonPayload = jsonNode?.ToJsonString() ?? JsonSerializer.Serialize(serverCommand);
            return System.Text.Encoding.UTF8.GetBytes(jsonPayload);
        }
    }
}
