using CommunityToolkit.Mvvm.ComponentModel;

namespace RLIRL.App.Models
{
    public partial class GameInfo : ObservableObject
    {
        [ObservableProperty]
        public partial int BlueScore { get; set; }

        [ObservableProperty]
        public partial int RedScore { get; set; }

        [ObservableProperty]
        public partial string TimeLeft { get; set; } = "00:00";

        [ObservableProperty]
        public partial DateTime StartTime { get; set; }

        [ObservableProperty]
        public partial DateTime EndTime { get; set; }

        [ObservableProperty]
        public partial bool IsGameActive { get; set; }
    }
}