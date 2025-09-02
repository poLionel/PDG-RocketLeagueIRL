using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Models;
using System.Runtime.CompilerServices;
using System.Text;

namespace RLIRL.Server.Services
{
    internal partial class ServerCameraFeedEncoder : IServerCameraFeedEncoder, IDisposable
    {
        private readonly object _currentFrameLock = new();
        private readonly object _taskCompletionSourceLock = new();
        private readonly object _singletonStreamLock = new();
        
        private CameraFrame? _currentFrame;
        private TaskCompletionSource _taskCompletionSource = new();
        private MjpegStream? _singletonStream;
        private bool _disposed;

        public Stream GetCurrentCameraFeed(CancellationToken cancellationToken = default)
        {
            ObjectDisposedException.ThrowIf(_disposed, this);
            
            lock (_singletonStreamLock)
            {
                // Return the existing stream if it's still valid, otherwise create a new one
                if (_singletonStream == null || _singletonStream.IsDisposed)
                {
                    _singletonStream = new MjpegStream(GetMjpegStreamAsyncInternal(cancellationToken));
                }
                
                return _singletonStream;
            }
        }

        public void UpdateLastFrame(string base64jpeg, double timestamp)
        {
            if (_disposed) return;
            
            if (string.IsNullOrEmpty(base64jpeg))
                return;

            TaskCompletionSource? oldTaskCompletionSource = null;

            lock (_currentFrameLock)
            {
                _currentFrame = new CameraFrame
                {
                    ImageData = base64jpeg,
                    Timestamp = timestamp,
                    ReceivedAt = DateTime.UtcNow
                };
            }

            // Signal that a new frame is available (outside the frame lock to avoid deadlocks)
            lock (_taskCompletionSourceLock)
            {
                oldTaskCompletionSource = _taskCompletionSource;
                _taskCompletionSource = new TaskCompletionSource();
            }

            // Signal outside of both locks
            oldTaskCompletionSource?.TrySetResult();
        }

        private async IAsyncEnumerable<byte[]> GetMjpegStreamAsyncInternal([EnumeratorCancellation] CancellationToken cancellationToken = default)
        {
            const string boundary = "frame";
            var boundaryBytes = Encoding.UTF8.GetBytes($"\r\n--{boundary}\r\n");
            var headerBytes = Encoding.UTF8.GetBytes("Content-Type: image/jpeg\r\nContent-Length: ");
            var newlineBytes = Encoding.UTF8.GetBytes("\r\n\r\n");

            while (!cancellationToken.IsCancellationRequested && !_disposed)
            {
                var frameData = GetCurrentFrameData();
                if (frameData != null)
                {
                    // Create MJPEG frame
                    var lengthBytes = Encoding.UTF8.GetBytes(frameData.Length.ToString());

                    var frameBuffer = new byte[boundaryBytes.Length + headerBytes.Length +
                                             lengthBytes.Length + newlineBytes.Length + frameData.Length];

                    var offset = 0;
                    Array.Copy(boundaryBytes, 0, frameBuffer, offset, boundaryBytes.Length);
                    offset += boundaryBytes.Length;

                    Array.Copy(headerBytes, 0, frameBuffer, offset, headerBytes.Length);
                    offset += headerBytes.Length;

                    Array.Copy(lengthBytes, 0, frameBuffer, offset, lengthBytes.Length);
                    offset += lengthBytes.Length;

                    Array.Copy(newlineBytes, 0, frameBuffer, offset, newlineBytes.Length);
                    offset += newlineBytes.Length;

                    Array.Copy(frameData, 0, frameBuffer, offset, frameData.Length);

                    yield return frameBuffer;
                }

                // Wait for next frame with proper synchronization
                Task waitTask;
                lock (_taskCompletionSourceLock)
                {
                    waitTask = _taskCompletionSource.Task;
                }

                try
                {
                    await waitTask.WaitAsync(cancellationToken);
                }
                catch (TimeoutException)
                {
                    // Continue on timeout
                }
                catch (OperationCanceledException)
                {
                    // Exit on cancellation
                    break;
                }
            }
        }

        private byte[]? GetCurrentFrameData()
        {
            if (_disposed) return null;
            
            lock (_currentFrameLock)
            {
                if (_currentFrame?.ImageData == null)
                    return null;

                try
                {
                    return Convert.FromBase64String(_currentFrame.ImageData);
                }
                catch (FormatException)
                {
                    return null;
                }
            }
        }

        public void Dispose()
        {
            if (_disposed) return;
            
            _disposed = true;
            
            lock (_singletonStreamLock)
            {
                _singletonStream?.Dispose();
                _singletonStream = null;
            }
            
            lock (_taskCompletionSourceLock)
            {
                _taskCompletionSource.TrySetCanceled();
            }
        }
    }
}