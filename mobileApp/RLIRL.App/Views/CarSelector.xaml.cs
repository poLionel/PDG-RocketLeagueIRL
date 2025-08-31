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

    private void OnBlueTeamPointerEntered(object? sender, PointerEventArgs e)
    {
        if (_viewModel.IsBlueTeamAvailable && !_viewModel.IsLoading)
        {
            // Brighten the blue team zone on hover
            BlueTeamBorder.BackgroundColor = Colors.RoyalBlue; // Slightly brighter blue
            BlueTeamBorder.Scale = 1.02; // Slight scale effect
        }
    }

    private void OnBlueTeamPointerExited(object? sender, PointerEventArgs e)
    {
        if (_viewModel.IsBlueTeamAvailable && !_viewModel.IsLoading)
        {
            // Reset to original blue color
            BlueTeamBorder.BackgroundColor = Color.FromArgb("#4169E1"); // GameBlue
            BlueTeamBorder.Scale = 1.0; // Reset scale
        }
    }

    private void OnRedTeamPointerEntered(object? sender, PointerEventArgs e)
    {
        if (_viewModel.IsRedTeamAvailable && !_viewModel.IsLoading)
        {
            // Brighten the red team zone on hover
            RedTeamBorder.BackgroundColor = Colors.Crimson; // Slightly brighter red
            RedTeamBorder.Scale = 1.02; // Slight scale effect
        }
    }

    private void OnRedTeamPointerExited(object? sender, PointerEventArgs e)
    {
        if (_viewModel.IsRedTeamAvailable && !_viewModel.IsLoading)
        {
            // Reset to original red color
            RedTeamBorder.BackgroundColor = Color.FromArgb("#DC143C"); // GameRed
            RedTeamBorder.Scale = 1.0; // Reset scale
        }
    }
}