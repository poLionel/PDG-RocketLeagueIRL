using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using RLIRL.App.Models;
using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Business.Services;
using RLIRL.Server.Abstractions.ClientCommands;
using System.Diagnostics;

namespace RLIRL.App.ViewModels
{
    public partial class GameViewModel : ObservableObject, IDisposable
    {
        #region Constructor

        public GameViewModel(ICarControlService carControlService, IGameService gameService, ITimerService timerService)
        {
            _carControlService = carControlService;
            _gameService = gameService;
            _timerService = timerService;

            _gameService.GameStatusChanged += OnGameStatusChanged;
            _timerService.TimeLeftChanged += OnTimerChanged;
            
        }

        #endregion

        #region Commands 

        [RelayCommand]
        private void AcceleratePressed()
        {
            _carControlService.SetDirection(Direction.Forward);
            IsClicked = true;

            Trace.WriteLine("CA clique");
        }

        [RelayCommand]
        private void AccelerateRelease() => _carControlService.SetDirection(Direction.Stopped);

        [RelayCommand]
        private void BrakePressed() => _carControlService.SetDirection(Direction.Backward);

        [RelayCommand]
        private void BrakeRelease() => _carControlService.SetDirection(Direction.Stopped);

        [RelayCommand]
        private void SetBoost(bool isActive) => _carControlService.SetBoost(isActive);

        //TODO joystick

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
            if (e != null)
                Game ??= new();
            else
                Game = new GameInfo();
        }

        private void OnTimerChanged(object? sender, TimeSpan e)
        {
            Timer = e.ToString(@"m\:ss");
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

        #endregion

        #region Private Fields

        private readonly ICarControlService _carControlService;

        private readonly IGameService _gameService;

        private readonly ITimerService _timerService;

        #endregion
    }
}
