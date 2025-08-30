using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;

namespace RLIRL.App.ViewModels
{
    public partial class GameViewModel : ObservableObject
    {
        #region Constructor

        public GameViewModel(ICarControlService carControlService) 
        {
            _carControlService = carControlService;

            //TODO instantiate timer 
        }

        #endregion

        #region Commands 

        [RelayCommand]
        private void AcceleratePressed() => Direction = Directions.Forward;

        [RelayCommand]
        private void AccelerateRelease() => Direction = Directions.Stopped;

        [RelayCommand]
        private void BrakePressed() => Direction = Directions.Backward; //TODO maybe change logic

        [RelayCommand]
        private void BrakeRelease() => Direction = Directions.Stopped;

        [RelayCommand]
        private void SetBoost(bool isActive) => IsBoosting = isActive;

        //TODO joystick

        #endregion

        #region Properties

        [ObservableProperty]
        private bool _isBoosting;

        [ObservableProperty]
        private int _steering;

        [ObservableProperty]
        private Directions _direction;

        #endregion

        #region Private Fields

        private readonly ICarControlService _carControlService;

        #endregion
    }
}
