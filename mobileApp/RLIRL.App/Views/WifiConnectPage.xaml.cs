namespace RLIRL.App.Views;

public partial class WifiConnectPage : ContentPage
{
	public WifiConnectPage()
	{
		InitializeComponent();
	}

    /// <summary>
    /// Go to the menu page when clicked. Temporary.
    /// </summary>
    /// <param name="sender"></param>
    /// <param name="e"></param>
    private void OnClickedButton(object sender, EventArgs e)
    {
        Shell.Current.GoToAsync("//menu");
    }
}