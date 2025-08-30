using RLIRL.App.ViewModels;

namespace RLIRL.App.Views;

public partial class WifiConnectPage : ContentPage
{
	public WifiConnectPage()
	{
		InitializeComponent();
        BindingContext = Application.Current?.Handler.MauiContext?.Services.GetRequiredService<WifiConnectViewModel>();
    }
}