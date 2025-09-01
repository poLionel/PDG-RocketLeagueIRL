using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Reflection;
using System.Text.Json;

namespace RLIRL.Server.Services
{
    internal class ServerCommandSerializer : IServerCommandSerializer
    {
        private static readonly JsonSerializerOptions _jsonOptions = new()
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            WriteIndented = false,
            Converters = { new System.Text.Json.Serialization.JsonStringEnumConverter() }
        };

        public byte[] SerializeCommand(IClientCommand serverCommand)
        {
            // Create an anonymous object that includes the action
            var action = serverCommand.GetType().GetCustomAttribute<CommandNameAttribute>()?.Name;

            // Serialize the command first
            var commandJson = JsonSerializer.Serialize(serverCommand, _jsonOptions);

            // If we have an action, we need to merge it in
            if (action != null)
            {
                var commandObject = JsonSerializer.Deserialize<JsonElement>(commandJson);
                var resultObject = new Dictionary<string, object> { ["action"] = action };

                // Add all properties from the command
                foreach (var property in commandObject.EnumerateObject())
                {
                    resultObject[property.Name] = property.Value;
                }

                commandJson = JsonSerializer.Serialize(resultObject, _jsonOptions);
            }

            return System.Text.Encoding.UTF8.GetBytes(commandJson);
        }
    }
}