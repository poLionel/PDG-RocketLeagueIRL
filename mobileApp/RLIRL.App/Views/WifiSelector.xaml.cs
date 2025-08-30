using RLIRL.App.ViewModels;

namespace RLIRL.App.Views;

public partial class WifiSelector : ContentView
{
	public WifiSelector()
	{
		InitializeComponent();
        BindingContext = Application.Current?.Handler.MauiContext?.Services.GetRequiredService<WifiSelectorViewModel>();
    }
}