using RLIRL.Server.Abstractions.Abstractions;
using System.Runtime.CompilerServices;
using System.Text;

namespace RLIRL.Server.Services
{
    internal partial class ServerCameraFeedEncoder : IServerCameraFeedEncoder
    {
        private readonly object _currentFrameLock = new();
        private CameraFrame? _currentFrame;

        public Stream? GetCurrentCameraFeed()
        {
            lock (_currentFrameLock)
            {
                if (_currentFrame?.ImageData == null)
                    return null;

                try
                {
                    var imageBytes = Convert.FromBase64String(_currentFrame.ImageData);
                    return new MemoryStream(imageBytes);
                }
                catch (FormatException)
                {
                    return null;
                }
            }
        }

        public void UpdateLastFrame(string base64jpeg, double timestamp)
        {
            if (string.IsNullOrEmpty(base64jpeg))
                return;

            lock (_currentFrameLock)
            {
                _currentFrame = new CameraFrame
                {
                    ImageData = base64jpeg,
                    Timestamp = timestamp,
                    ReceivedAt = DateTime.UtcNow
                };
            }
        }

        public async IAsyncEnumerable<byte[]> GetMjpegStreamAsync([EnumeratorCancellation] CancellationToken cancellationToken = default)
        {
            const string boundary = "frame";
            var boundaryBytes = Encoding.UTF8.GetBytes($"\r\n--{boundary}\r\n");
            var headerBytes = Encoding.UTF8.GetBytes("Content-Type: image/jpeg\r\nContent-Length: ");
            var newlineBytes = Encoding.UTF8.GetBytes("\r\n\r\n");

            while (!cancellationToken.IsCancellationRequested)
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

                // Wait for next frame
                await Task.Delay(33, cancellationToken); // ~30 FPS
            }
        }

        private byte[]? GetCurrentFrameData()
        {
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
    }
}