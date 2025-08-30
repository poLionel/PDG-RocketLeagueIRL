using CommunityToolkit.Mvvm.ComponentModel;

namespace RLIRL.App.Models
{
    public partial class CarInfo : ObservableObject
    {
        [ObservableProperty]
        public partial int CarId { get; set; }

        [ObservableProperty]
        public partial string Status { get; set; } = "Disconnected";

        [ObservableProperty]
        public partial bool IsConnected { get; set; }

        [ObservableProperty]
        public partial bool IsAssigned { get; set; }

        [ObservableProperty]
        public partial string AssignedPlayer { get; set; } = string.Empty;

        [ObservableProperty]
        public partial string Team { get; set; } = string.Empty;

        [ObservableProperty]
        public partial string TeamColor { get; set; } = "Gray";

        [ObservableProperty]
        public partial int BatteryLevel { get; set; }

        [ObservableProperty]
        public partial string BleAddress { get; set; } = string.Empty;
    }
}