using AutoMapper;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using RLIRL.App.Models;
using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Business.Services;
using RLIRL.Server.Abstractions.ClientCommands;
using RLIRL.Server.Abstractions.ServerResponses;

namespace RLIRL.App.ViewModels
{
    public partial class GameViewModel : ObservableObject, IDisposable
    {
        #region Constructor

        public GameViewModel(ICarControlService carControlService, IGameService gameService, ITimerService timerService, ICarService carService, ICameraFeedService cameraFeedService, IMapper mapper)
        {
            _carControlService = carControlService;
            _gameService = gameService;
            _timerService = timerService;
            _carService = carService;
            _cameraFeedService = cameraFeedService;
            _mapper = mapper;

            _gameService.GameStatusChanged += OnGameStatusChanged;
            _timerService.TimeLeftChanged += OnTimerChanged;
            _carService.CurrentCarChanged += OnCurrentCarChanged;
            _cameraFeedService.CameraFeedsChanged += OnCameraFeedsChanged;

            cameraFeedService.Refresh();
        }

        #endregion

        #region Commands 

        [RelayCommand]
        private void AcceleratePressed()
        {
            _carControlService.SetDirection(Direction.Forward);
            IsClicked = true;
        }

        [RelayCommand]
        private void AccelerateRelease()
        {
            _carControlService.SetDirection(Direction.Stopped);
            IsClicked = false;
        }

        [RelayCommand]
        private void BrakePressed() => _carControlService.SetDirection(Direction.Backward);

        [RelayCommand]
        private void BrakeRelease() => _carControlService.SetDirection(Direction.Stopped);

        [RelayCommand]
        private void SetBoost(bool isActive) => _carControlService.SetBoost(isActive);

        [RelayCommand]
        private void SetSteering(int value)
        {
            value = Math.Clamp(value, -100, 100);
            Steering = value;
            _carControlService.SetSteering(value);
        }

        #endregion

        #region Methods

        /// <inheritdoc />
        public void Dispose()
        {
            _gameService.GameStatusChanged -= OnGameStatusChanged;
            _timerService.TimeLeftChanged -= OnTimerChanged;
        }


        private void OnGameStatusChanged(object? sender, GameStatus? e)
        {
            // Ensure UI updates happen on the main thread
            MainThread.BeginInvokeOnMainThread(() =>
            {
                if (e != null)
                    Game ??= new();
                else
                    Game = new GameInfo();
            });
        }

        private void OnTimerChanged(object? sender, TimeSpan e)
        {
            // Ensure UI updates happen on the main thread
            MainThread.BeginInvokeOnMainThread(() =>
            {
                Timer = e.ToString(@"m\:ss");
            });
        }

        private void UpdateCameraWebViewSource()
        {
            var carId = _carService.CurrentCar;
            if (carId.HasValue)
            {
                var feed = _cameraFeedService.CameraFeeds.FirstOrDefault(f => f.CarId == carId.Value);
                if (feed != null && !string.IsNullOrEmpty(feed.Url))
                {
                    CameraWebViewSource = CreateWebViewSource(feed.Url);
                    return;
                }
            }
            CameraWebViewSource = null;
        }

        private static WebViewSource CreateWebViewSource(string url)
        {
            return new HtmlWebViewSource
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
            overflow: hidden;
        }}
        .container {{ 
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            width: 100vw;
        }}
        img {{ 
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            background: #000;
        }}
    </style>
</head>
<body>
    <div class='container'>
        <img src='{url}' alt='Camera Feed' />
    </div>
</body>
</html>
"
            };
        }

        private void OnCurrentCarChanged(object? sender, int? carId)
        {
            MainThread.BeginInvokeOnMainThread(UpdateCameraWebViewSource);
        }

        private void OnCameraFeedsChanged(object? sender, IEnumerable<CameraFeed> feeds)
        {
            MainThread.BeginInvokeOnMainThread(UpdateCameraWebViewSource);
        }

        #endregion

        #region Properties

        [ObservableProperty]
        public partial bool IsBoosting { get; set; } //TODO need to use it for SetBoost

        [ObservableProperty]
        public partial int Steering { get; set; }

        [ObservableProperty]
        public partial Direction Direction { get; set; }

        [ObservableProperty]
        public partial GameInfo Game { get; set; } = new();

        [ObservableProperty]
        public partial string Timer { get; set; } = "5:00";

        [ObservableProperty]
        public partial bool IsClicked { get; set; } = false;

        [ObservableProperty]
        public partial WebViewSource? CameraWebViewSource { get; set; }

        #endregion

        #region Private Fields

        private readonly ICarControlService _carControlService;

        private readonly IGameService _gameService;

        private readonly ITimerService _timerService;

        private readonly ICarService _carService;

        private readonly ICameraFeedService _cameraFeedService;

        private readonly IMapper _mapper;

        #endregion
    }
}
