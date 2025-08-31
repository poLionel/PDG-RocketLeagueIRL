using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using RLIRL.Business.Abstractions.Abstractions;

namespace RLIRL.App.ViewModels
{
    public partial class CarSelectorViewModel : ObservableObject, IDisposable
    {
        [ObservableProperty]
        public partial int BlueTeamCarsAvailable { get; set; }

        [ObservableProperty]
        public partial int RedTeamCarsAvailable { get; set; }

        [ObservableProperty]
        public partial bool IsBlueTeamAvailable { get; set; }

        [ObservableProperty]
        public partial bool IsRedTeamAvailable { get; set; }

        [ObservableProperty]
        public partial bool IsLoading { get; set; }

        [ObservableProperty]
        public partial bool HasAnyCarsAvailable { get; set; }

        private readonly ICarService _carService;

        public CarSelectorViewModel(ICarService carService)
        {
            _carService = carService;
            
            // Subscribe to car service events
            _carService.FreeCarsChanged += OnFreeCarsChanged;
            _carService.CurrentCarChanged += OnCurrentCarChanged;
            
            // Initialize with current data
            UpdateAvailableCars();
        }

        [RelayCommand]
        private void JoinBlueTeam()
        {
            if (!IsBlueTeamAvailable || IsLoading) return;
            
            IsLoading = true;

            // TODO : Filter cars by team when backend supports it
            var availableCars = _carService.FreeCars.ToList();
            if (availableCars.Count == 0) return;

            _carService.SelectCar(availableCars[0]);
        }

        [RelayCommand]
        private void JoinRedTeam()
        {
            if (!IsRedTeamAvailable || IsLoading) return;
            
            IsLoading = true;

            // TODO : Filter cars by team when backend supports it
            var availableCars = _carService.FreeCars.ToList();
            if (availableCars.Count <= 0) return;

            _carService.SelectCar(availableCars[0]);
        }

        private void OnFreeCarsChanged(object? sender, IEnumerable<int> freeCars)
        {
            UpdateAvailableCars();
        }

        private void OnCurrentCarChanged(object? sender, int? currentCar)
        {
            IsLoading = false;
            
            if (currentCar.HasValue)
            {
                // Car was assigned, navigate to game page
                MainThread.BeginInvokeOnMainThread(async () =>
                {
                    await Shell.Current.GoToAsync("//game");
                });
            }
        }

        private void UpdateAvailableCars()
        {
            var totalCars = _carService.FreeCars.Count();

            // Distribute cars evenly between teams for now as backend does not support team-based car assignment
            // TODO : Update logic when backend supports team-based car assignment
            BlueTeamCarsAvailable = totalCars / 2;
            RedTeamCarsAvailable = totalCars - BlueTeamCarsAvailable;
            
            IsBlueTeamAvailable = BlueTeamCarsAvailable > 0;
            IsRedTeamAvailable = RedTeamCarsAvailable > 0;
            HasAnyCarsAvailable = totalCars > 0;
        }

        public void Dispose()
        {
            _carService.FreeCarsChanged -= OnFreeCarsChanged;
            _carService.CurrentCarChanged -= OnCurrentCarChanged;
        }
    }
}