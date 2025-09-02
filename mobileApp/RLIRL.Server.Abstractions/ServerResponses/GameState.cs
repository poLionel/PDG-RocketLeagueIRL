using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerResponses
{
    public enum GameState
    {
        [JsonPropertyName("not_started")]
        NotStarted,

        [JsonPropertyName("active")]
        Active,

        [JsonPropertyName("paused")]
        Paused,

        [JsonPropertyName("ended")]
        Ended,
    }
}
