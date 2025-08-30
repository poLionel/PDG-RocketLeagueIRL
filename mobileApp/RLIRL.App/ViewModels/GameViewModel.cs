using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions.ClientCommands;

namespace RLIRL.App.ViewModels
{
    public partial class GameViewModel : ObservableObject, IDisposable, IGameService
    {
        #region Constructor

        public GameViewModel(ICarControlService carControlService) 
        {
            _carControlService = carControlService;
            //_gameService = gameService;
            Timer = string.Empty;
        }

        #endregion

        #region Commands 

        [RelayCommand]
        private void AcceleratePressed() => _carControlService.SetDirection(Directions.Forward);

        [RelayCommand]
        private void AccelerateRelease() => _carControlService.SetDirection(Directions.Stopped);

        [RelayCommand]
        private void BrakePressed() => _carControlService.SetDirection(Directions.Backward); //TODO maybe change logic

        [RelayCommand]
        private void BrakeRelease() => _carControlService.SetDirection(Directions.Stopped);

        [RelayCommand]
        private void SetBoost(bool isActive) => _carControlService.SetBoost(isActive);

        //TODO joystick

        #endregion

        #region Methods

        /// <inheritdoc />
        public void Dispose()
        {
            throw new NotImplementedException();
        }

        public void UpdateGameStatus(GameStatus? status)
        {
            throw new NotImplementedException();
        }

        #endregion

        #region Properties

        [ObservableProperty]
        private bool _isBoosting;

        [ObservableProperty]
        private int _steering;

        [ObservableProperty]
        private Directions _direction;

        [ObservableProperty]
        private int scoreTeamA;

        [ObservableProperty]
        private int scoreTeamB;

        [ObservableProperty]
        private string timer;

        #endregion

        #region Private Fields

        private readonly ICarControlService _carControlService;

        private readonly IGameService _gameService;

        #endregion

        public event EventHandler<GameStatus?>? GameStatusChanged;

        public GameStatus? CurrentGameStatus => throw new NotImplementedException();
    }
}
