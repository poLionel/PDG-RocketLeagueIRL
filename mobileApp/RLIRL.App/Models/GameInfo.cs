using CommunityToolkit.Mvvm.ComponentModel;
using RLIRL.Server.Abstractions.ServerResponses;

namespace RLIRL.App.Models
{
    public partial class GameInfo : ObservableObject
    {
        [ObservableProperty]
        public partial int BlueScore { get; set; }

        [ObservableProperty]
        public partial int RedScore { get; set; }

        [ObservableProperty]
        public partial int MatchLengthSeconds { get; set; }

        [ObservableProperty]
        public partial DateTime? StartTime { get; set; }

        [ObservableProperty]
        public partial int PauseTime { get; set; }

        [ObservableProperty]
        public partial GameState State { get; set; }

        [ObservableProperty]
        public partial string StateMessage { get; set; }
    }
}