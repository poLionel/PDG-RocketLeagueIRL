using RLIRL.App.ViewModels;
using RLIRL.App.Helper;

namespace RLIRL.App.Views;

public partial class CarSelector : ContentView
{
    private readonly CarSelectorViewModel _viewModel;

    public CarSelector()
    {
        InitializeComponent();
        _viewModel = ServiceHelper.Get<CarSelectorViewModel>();
        BindingContext = _viewModel;
    }
}