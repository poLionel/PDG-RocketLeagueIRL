using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using RLIRL.App.Models;
using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions.ClientCommands;
using RLIRL.Server.Abstractions.ServerResponses;

namespace RLIRL.App.ViewModels
{
    public partial class GameViewModel : ObservableObject, IDisposable
    {
        #region Constructor

        public GameViewModel(ICarControlService carControlService, IGameService gameService) 
        {
            _carControlService = carControlService;
            _gameService = gameService;

            _gameService.GameStatusChanged += OnGameStatusChanged;
        }

        #endregion

        #region Commands 

        [RelayCommand]
        private void AcceleratePressed() => _carControlService.SetDirection(Server.Abstractions.ClientCommands.Direction.Forward);

        [RelayCommand]
        private void AccelerateRelease() => _carControlService.SetDirection(Server.Abstractions.ClientCommands.Direction.Stopped);

        [RelayCommand]
        private void BrakePressed() => _carControlService.SetDirection(Server.Abstractions.ClientCommands.Direction.Backward); //TODO maybe change logic

        [RelayCommand]
        private void BrakeRelease() => _carControlService.SetDirection(Server.Abstractions.ClientCommands.Direction.Stopped);

        [RelayCommand]
        private void SetBoost(bool isActive) => _carControlService.SetBoost(isActive);

        //TODO joystick

        #endregion

        #region Methods

        /// <inheritdoc />
        public void Dispose()
        {
            _gameService.GameStatusChanged -= OnGameStatusChanged;
        }


        public void OnGameStatusChanged(object? sender, GameStatus? e)
        {
            if (e == null)
                Game ??= new();
            else
                Game = new GameInfo();
        }

        #endregion

        #region Properties

        [ObservableProperty]
        public partial bool IsBoosting { get; set; }

        [ObservableProperty]
        public partial int Steering { get; set; }

        [ObservableProperty]
        public partial Direction Direction { get; set; }

        [ObservableProperty]
        public partial GameInfo Game { get; set; } = new();

        #endregion

        #region Private Fields

        private readonly ICarControlService _carControlService;

        private readonly IGameService _gameService;

        #endregion


    }
}
