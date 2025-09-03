using RLIRL.App.Helper;
using RLIRL.App.ViewModels;

namespace RLIRL.App.Views;

public partial class GameAdminPage : ContentPage
{
    public GameAdminPage()
    {
        BindingContext = ServiceHelper.Get<GameAdminViewModel>();
        InitializeComponent();
    }

    protected override void OnAppearing()
    {
        base.OnAppearing();
        
        if (BindingContext is GameAdminViewModel viewModel)
        {
            viewModel.Initialize();
        }
    }
}