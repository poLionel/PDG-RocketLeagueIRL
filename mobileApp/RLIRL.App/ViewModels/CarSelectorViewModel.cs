using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using RLIRL.Business.Abstractions.Abstractions;

namespace RLIRL.App.ViewModels
{
    public partial class CarSelectorViewModel : ObservableObject, IDisposable
    {
        private const int LOADING_TIMEOUT_MS = 2000;

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
        private CancellationTokenSource? _loadingCancellationTokenSource;

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

            SetLoading();

            // TODO : Filter cars by team when backend supports it
            var availableCars = _carService.FreeCars.ToList();
            if (availableCars.Count == 0) 
            {
                SetNotLoading();
                return;
            }

            _carService.SelectCar(availableCars[0]);
        }

        [RelayCommand]
        private void JoinRedTeam()
        {
            if (!IsRedTeamAvailable || IsLoading) return;

            SetLoading();

            // TODO : Filter cars by team when backend supports it
            var availableCars = _carService.FreeCars.ToList();
            if (availableCars.Count <= 0) 
            {
                SetNotLoading();
                return;
            }

            _carService.SelectCar(availableCars[0]);
        }

        private void SetLoading()
        {
            if (IsLoading) return;

            IsLoading = true;

            // Cancel any existing loading timeout
            _loadingCancellationTokenSource?.Cancel();
            _loadingCancellationTokenSource?.Dispose();

            // Set loading state with a timeout to avoid indefinite loading
            _loadingCancellationTokenSource = new CancellationTokenSource();
            
            // Start timeout task
            _ = Task.Run(async () =>
            {
                try
                {
                    await Task.Delay(LOADING_TIMEOUT_MS, _loadingCancellationTokenSource.Token);
                    MainThread.BeginInvokeOnMainThread(() => SetNotLoading());
                }
                catch (OperationCanceledException)
                {
                    // Expected when cancelled, do nothing
                }
            });
        }

        private void SetNotLoading()
        {
            if (!IsLoading) return;

            _loadingCancellationTokenSource?.Cancel();
            _loadingCancellationTokenSource?.Dispose();
            _loadingCancellationTokenSource = null;
            
            IsLoading = false;
        }

        private void OnFreeCarsChanged(object? sender, IEnumerable<int> freeCars)
        {
            // Ensure UI updates happen on the main thread
            MainThread.BeginInvokeOnMainThread(() =>
            {
                UpdateAvailableCars();
            });
        }

        private void OnCurrentCarChanged(object? sender, int? currentCar)
        {
            // Ensure UI updates happen on the main thread
            MainThread.BeginInvokeOnMainThread(() =>
            {
                SetNotLoading();
                
                if (currentCar.HasValue)
                {
                    // Car was assigned, navigate to game page
                    Shell.Current.GoToAsync("//game");
                }
            });
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
            
            _loadingCancellationTokenSource?.Cancel();
            _loadingCancellationTokenSource?.Dispose();
        }
    }
}