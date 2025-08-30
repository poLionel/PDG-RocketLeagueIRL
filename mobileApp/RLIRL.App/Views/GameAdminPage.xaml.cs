using RLIRL.App.ViewModels;

namespace RLIRL.App.Views;

public partial class GameAdminPage : ContentPage
{
    public GameAdminPage()
    {
        InitializeComponent();
    }

    public GameAdminPage(GameAdminViewModel viewModel) : this()
    {
        BindingContext = viewModel;
    }

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        
        if (BindingContext is GameAdminViewModel viewModel)
        {
            await viewModel.InitializeAsync();
        }
    }
}