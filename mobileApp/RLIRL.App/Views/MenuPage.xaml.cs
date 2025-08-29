namespace RLIRL.App.Views;

public partial class MenuPage : ContentPage
{
	public MenuPage()
	{
		InitializeComponent();
	}

	/// <summary>
	/// Go to the game view. Temporary
	/// </summary>
	/// <param name="sender"></param>
	/// <param name="e"></param>
	private void OnPlay(object sender, EventArgs e)
	{
		Shell.Current.GoToAsync("//game");
	}

	private void OnConnect(object sender, EventArgs e)
	{
		// Does nothing
	}

	private void OnSpectate(object sender, EventArgs e)
	{
		// Does nothing
	}
}