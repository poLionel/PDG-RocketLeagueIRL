using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using RLIRL.Server.Abstractions.ClientCommands;
using RLIRL.Server.Services;
using System.Text.Json;
using Xunit;

namespace RLIRL.Server.Tests.Services
{
    public class ServerCommandSerializerTests
    {
        private readonly ServerCommandSerializer _serializer;

        public ServerCommandSerializerTests()
        {
            _serializer = new ServerCommandSerializer();
        }

        [Fact]
        public void SerializeCommand_WithGetFreeCarsCommand_ReturnsCorrectJson()
        {
            // Arrange
            var command = new GetFreeCarsCommand();

            // Act
            var result = _serializer.SerializeCommand(command);

            // Assert
            var json = System.Text.Encoding.UTF8.GetString(result);
            var deserialized = JsonSerializer.Deserialize<Dictionary<string, object>>(json);
            
            Assert.NotNull(deserialized);
            Assert.True(deserialized.ContainsKey("action"));
            Assert.Equal("get_free_cars", deserialized["action"].ToString());
        }

        [Fact]
        public void SerializeCommand_WithMoveCarCommand_ReturnsCorrectJson()
        {
            // Arrange
            var command = new MoveCarCommand
            {
                Car = 1,
                Direction = Direction.Forward,
                Steering = 15,
                Boost = true
            };

            // Act
            var result = _serializer.SerializeCommand(command);

            // Assert
            var json = System.Text.Encoding.UTF8.GetString(result);
            var deserialized = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(json);
            
            Assert.NotNull(deserialized);
            Assert.True(deserialized.ContainsKey("action"));
            Assert.Equal("move_car", deserialized["action"].GetString());
            Assert.Equal(1, deserialized["car"].GetInt32());
            Assert.Equal(15, deserialized["x"].GetInt32());
            Assert.True(deserialized["boost"].GetBoolean());
        }

        [Fact]
        public void SerializeCommand_WithSelectCarCommand_ReturnsCorrectJson()
        {
            // Arrange
            var command = new SelectCarCommand
            {
                Car = 2
            };

            // Act
            var result = _serializer.SerializeCommand(command);

            // Assert
            var json = System.Text.Encoding.UTF8.GetString(result);
            var deserialized = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(json);
            
            Assert.NotNull(deserialized);
            Assert.True(deserialized.ContainsKey("action"));
            Assert.Equal("select_car", deserialized["action"].GetString());
            Assert.Equal(2, deserialized["car"].GetInt32());
        }

        [Fact]
        public void SerializeCommand_WithGoalScoredCommand_ReturnsCorrectJson()
        {
            // Arrange
            var command = new GoalScoredCommand
            {
                Team = "blue"
            };

            // Act
            var result = _serializer.SerializeCommand(command);

            // Assert
            var json = System.Text.Encoding.UTF8.GetString(result);
            var deserialized = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(json);
            
            Assert.NotNull(deserialized);
            Assert.True(deserialized.ContainsKey("action"));
            Assert.Equal("goal_scored", deserialized["action"].GetString());
            Assert.Equal("blue", deserialized["team"].GetString());
        }

        [Fact]
        public void SerializeCommand_ReturnsValidUtf8Bytes()
        {
            // Arrange
            var command = new GetFreeCarsCommand();

            // Act
            var result = _serializer.SerializeCommand(command);

            // Assert
            Assert.NotNull(result);
            Assert.True(result.Length > 0);
            
            // Should be able to decode back to string without exception
            var json = System.Text.Encoding.UTF8.GetString(result);
            Assert.False(string.IsNullOrEmpty(json));
        }
    }
}