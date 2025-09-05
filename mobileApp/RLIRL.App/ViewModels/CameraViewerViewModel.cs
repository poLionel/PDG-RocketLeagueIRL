using CommunityToolkit.Mvvm.ComponentModel;

namespace RLIRL.App.ViewModels
{
    public partial class CameraViewerViewModel : ObservableObject
    {
        [ObservableProperty]
        public partial WebViewSource? VideoStreamSource { get; set; }

        [ObservableProperty]
        public partial int? SelectedCameraFeedId { get; set; }

        [ObservableProperty]
        public partial bool IsLoading { get; set; }

        public void UpdateCamera(Uri? videoStreamUrl, int? cameraFeedId)
        {
            VideoStreamSource = CreateWebViewSource(videoStreamUrl);
            SelectedCameraFeedId = cameraFeedId;
        }

        public void ClearCamera()
        {
            VideoStreamSource = null;
            SelectedCameraFeedId = null;
        }

        private static WebViewSource? CreateWebViewSource(Uri? videoStreamUrl)
        {
            if (videoStreamUrl == null) return null;

            return new HtmlWebViewSource()
            {
                Html = $@"
<!DOCTYPE html>
<html>
<head>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <style>
        html, body {{
            height: 100%;
            margin: 0;
            padding: 0;
            background: #000;
        }}
        .container {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            width: 100vw;
        }}
        img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            display: block;
            background: #000;
        }}
    </style>
</head>
<body>
    <div class='container'>
        <img src='{videoStreamUrl}' alt='Camera Feed' />
    </div>
</body>
</html>
"
            };
        }
    }
}