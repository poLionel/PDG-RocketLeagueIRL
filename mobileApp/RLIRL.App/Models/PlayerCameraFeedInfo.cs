using CommunityToolkit.Mvvm.ComponentModel;

namespace RLIRL.App.Models
{
    public partial class PlayerCameraFeedInfo : ObservableObject
    {
        [ObservableProperty]
        public partial string PlayerName { get; set; } = string.Empty;

        [ObservableProperty]
        public partial int CarId { get; set; }

        [ObservableProperty]
        public partial string Team { get; set; } = string.Empty;

        [ObservableProperty]
        public partial string TeamColor { get; set; } = "Gray";

        [ObservableProperty]
        public partial bool IsSelected { get; set; }

        [ObservableProperty]
        public partial string VideoFeedUrl { get; set; } = string.Empty;
    }
}