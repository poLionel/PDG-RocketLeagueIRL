using CommunityToolkit.Mvvm.ComponentModel;

namespace RLIRL.App.Models
{
    public partial class CameraFeedItem : ObservableObject
    {
        public int CarId { get; set; }
        public required string Url { get; set; }
        
        [ObservableProperty]
        public partial bool IsSelected { get; set; }
    }
}
