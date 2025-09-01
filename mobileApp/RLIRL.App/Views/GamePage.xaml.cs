using RLIRL.App.Helper;
using RLIRL.App.ViewModels;

namespace RLIRL.App.Views;

/// <summary>
/// MAUI game page that renders the HUD and handles touch interactions
/// (virtual joystick and speed/boost). The page computes the joystick X axis,
/// quantizes it (steps), and sends it to the <see cref="GameViewModel.SetSteeringCommand"/>
/// with a small throttle to avoid overloading the server.
/// </summary>
public partial class GamePage : ContentPage
{

    #region Constructor

    /// <summary>
    /// Initializes the page, sets the binding context to a
    /// <see cref="GameViewModel"/>, and forces landscape orientation on Android..
    /// </summary>
    public GamePage()
	{
		InitializeComponent();
		BindingContext = ServiceHelper.Services.GetService<GameViewModel>();

#if ANDROID
        _orientation = ServiceHelper.Get<IOrientationService>();
#endif
	}

    #endregion

    #region Methods

    /// <summary>
    /// Handles the joystick pan gesture.
    /// - Constrains the knob within the circular base.
    /// - Updates the knob position visually.
    /// - Converts the X displacement to a steering value (-100..100)
    ///   and sends it to the ViewModel using throttling/quantization.
    /// </summary>
    /// <param name="sender">The gesture source (the knob).</param>
    /// <param name="e">Pan gesture data (cumulative deltas and status).</param>
    public void OnJoystickPanUpdated(object? sender, PanUpdatedEventArgs e)
    {
        switch (e.StatusType)
        {
            case GestureStatus.Started:
                // Nothing special when the pan starts.
                break;

            case GestureStatus.Running:
                // Knob displacement from the center (in px).
                var dx = e.TotalX;
                var dy = e.TotalY;

                // Keep the knob inside the circle.
                var len = Math.Sqrt(dx * dx + dy * dy);
                var max = _joyRadius - _knobRadius; // margin to remain inside

                if (len > max && len > 0)
                {
                    var scale = max / len;
                    dx *= scale;
                    dy *= scale;
                }

                // Update the knob visual position.
                AbsoluteLayout.SetLayoutBounds(JoyKnob, new Rect(0.5 + dx / (2 * _joyRadius), 0.5 + dy / (2 * _joyRadius), 64, 64));

                // X axis only: normalize to -1..1, then scale to -100..100.
                var nx = (dx / max);
                var steering = (int)(nx * 100.0);

                // Send throttled + quantized value to the VM.
                SendSteeringThrottled(steering);

                break;

            case GestureStatus.Completed:
            case GestureStatus.Canceled:
                // Re-center the knob visually.
                AbsoluteLayout.SetLayoutBounds(JoyKnob, new Rect(.5, .5, 64, 64));
                // Cancel any pending emission and send "0" immediately.
                _steerCts?.Cancel();
                SendSteeringThrottled(0);
                break;
        }
    }

    /// <summary>
    /// Optional speed button pan (currently unused).
    /// Example idea: if the user drags upward beyond a threshold, enable boost.
    /// </summary>
    /// <param name="sender">The gesture source (the speed button).</param>
    /// <param name="e">Pan gesture data.</param>
    public void OnSpeedPanUpdated(object? sender, PanUpdatedEventArgs e)
    {
        if (BindingContext is not GameViewModel vm) return;

        if (e.StatusType == GestureStatus.Running)
        {
            // Dragging upward sets positive values.
            var dragUp = -e.TotalY;
            //vm.SetBoost(dragUp > BoostThreshold);
        }
        else if (e.StatusType is GestureStatus.Completed or GestureStatus.Canceled)
        {
            //vm.SetBoost(false);
        }
    }

    /// <summary>
    /// Forces landscape orientation on Android when the page appears.
    /// </summary>
    protected override void OnAppearing()
    {
        base.OnAppearing();

#if ANDROID
        _orientation?.Landscape();
#endif
    }

    /// <summary>
    /// Restores default orientation on Android when the page disappears.
    /// </summary>
    protected override void OnDisappearing()
    {
#if ANDROID
        _orientation?.Default();
#endif
        base.OnDisappearing();
    }

    #endregion

    #region Private methods

    /// <summary>
    /// Quantizes the input value (expected in -100..100) to the nearest step.
    /// For example with step=10: -100, -90, -80, ..., 0, 10, ..., 100.
    /// </summary>
    /// <param name="v">Raw value in the range -100..100.</param>
    /// <param name="step">Quantization step (e.g., 5 or 10).</param>
    /// <returns>Value snapped to the nearest multiple of <paramref name="step"/>.</returns>
    private static int Quantize(double v, int step) => (int)Math.Clamp(step * Math.Round(v / step), -100, 100);

    /// <summary>
    /// Sends the steering value to the ViewModel with throttling and coalescing:
    /// - At most one emission per <see cref="IntervalMs"/>.
    /// - If multiple values arrive within the window, only the last one is sent.
    /// - Values are quantized to <see cref="Step"/> to reduce server load.
    /// </summary>
    /// <param name="raw">Raw steering value (-100..100).</param>
    private void SendSteeringThrottled(int raw)
    {
        if (BindingContext is not GameViewModel vm) return;

        var v = Quantize(raw, Step);
        var now = DateTime.UtcNow;
        var elapsed = (now - _lastAt).TotalMilliseconds;

        // don't resend identical values at all
        if (v == _lastSent) return;

        void Emit(int val)
        {
            _lastSent = val;
            _lastAt = DateTime.UtcNow;
            if (vm.SetSteeringCommand.CanExecute(val))
                vm.SetSteeringCommand.Execute(val);
        }

        if (elapsed > IntervalMs)
        {
            Emit(v);
        }
        else
        {
            _steerCts?.Cancel();
            _steerCts = new CancellationTokenSource();
            var delay = IntervalMs - (int)elapsed;
            _ = Task.Run(async () =>
            {
                try { await Task.Delay(delay, _steerCts.Token); } catch { return; }
                MainThread.BeginInvokeOnMainThread(() =>
                {
                    if (v != _lastSent) // recheck to avoid duplicate if something emitted meanwhile
                        Emit(v);
                });
            });
        }
    }

    #endregion

    #region Private fields

    /// <summary>
    /// Base circle radius (in px) used to normalize knob movement.
    /// </summary>
    private double _joyRadius = 70;

    /// <summary>
    /// Knob radius (in px) used for clamping inside the base circle.
    /// </summary>
    private double _knobRadius = 32;

    /// <summary>
    /// Quantization step for steering values. Use 5 or 10.
    /// </summary>
    private const int Step = 10;

    /// <summary>
    /// Throttle interval in milliseconds for steering updates.
    /// </summary>
    private const int IntervalMs = 80;

    /// <summary>
    /// Last quantized value that was sent to the ViewModel.
    /// </summary>
    private int _lastSent = int.MinValue;

    /// <summary>
    /// Timestamp of the last emission (UTC) for throttling.
    /// </summary>
    private DateTime _lastAt = DateTime.MinValue;

    /// <summary>
    /// Cancellation token used to coalesce scheduled emissions.
    /// </summary>
    private CancellationTokenSource? _steerCts;

    /// <summary>
    /// Drag distance (px) above which boost could be considered active.
    /// </summary>
    const double BoostThreshold = 40;

    /// <summary>
    /// Orientation service (Android): forces landscape / restores default.
    /// </summary>
    private readonly IOrientationService _orientation;

    #endregion
}
