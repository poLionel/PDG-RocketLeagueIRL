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
    }
}