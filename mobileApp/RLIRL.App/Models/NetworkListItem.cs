using CommunityToolkit.Mvvm.ComponentModel;

namespace RLIRL.App.Models
{
    public partial class NetworkListItem : ObservableObject
    {
        [ObservableProperty]
        public partial string Ssid { get; set; }

        [ObservableProperty]
        public partial string? Icon { get; set; }

        [ObservableProperty]
        public partial bool Connected { get; set; }
    }
}
