namespace RLIRL.Server.Models
{
    /// <summary>
    /// A Stream implementation that wraps an IAsyncEnumerable of byte arrays for MJPEG streaming
    /// </summary>
    internal class MjpegStream : Stream
    {
        private readonly IAsyncEnumerator<byte[]> _enumerator;
        private byte[]? _currentBuffer;
        private int _currentPosition;
        private bool _disposed;
        private readonly CancellationTokenSource _cancellationTokenSource = new();

        public MjpegStream(IAsyncEnumerable<byte[]> source)
        {
            _enumerator = source.GetAsyncEnumerator(_cancellationTokenSource.Token);
        }

        public bool IsDisposed => _disposed;

        public override bool CanRead => !_disposed;
        public override bool CanSeek => false;
        public override bool CanWrite => false;
        public override long Length => throw new NotSupportedException();
        public override long Position
        {
            get => throw new NotSupportedException();
            set => throw new NotSupportedException();
        }

        public override async Task<int> ReadAsync(byte[] buffer, int offset, int count, CancellationToken cancellationToken)
        {
            if (_disposed)
                return 0;

            try
            {
                int totalBytesRead = 0;

                while (totalBytesRead < count && !cancellationToken.IsCancellationRequested && !_disposed)
                {
                    // If we don't have a current buffer or we've read all of it, get the next one
                    if (_currentBuffer == null || _currentPosition >= _currentBuffer.Length)
                    {
                        if (!await _enumerator.MoveNextAsync())
                        {
                            // No more data available
                            break;
                        }
                        _currentBuffer = _enumerator.Current;
                        _currentPosition = 0;
                    }

                    // Copy data from current buffer to output buffer
                    int bytesToCopy = Math.Min(count - totalBytesRead, _currentBuffer.Length - _currentPosition);
                    Array.Copy(_currentBuffer, _currentPosition, buffer, offset + totalBytesRead, bytesToCopy);

                    _currentPosition += bytesToCopy;
                    totalBytesRead += bytesToCopy;
                }

                return totalBytesRead;
            }
            catch (OperationCanceledException)
            {
                return 0;
            }
        }

        public override int Read(byte[] buffer, int offset, int count)
        {
            return ReadAsync(buffer, offset, count, CancellationToken.None).GetAwaiter().GetResult();
        }

        public override void Flush() { }
        public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
        public override void SetLength(long value) => throw new NotSupportedException();
        public override void Write(byte[] buffer, int offset, int count) => throw new NotSupportedException();

        protected override void Dispose(bool disposing)
        {
            if (!_disposed && disposing)
            {
                _disposed = true;
                _cancellationTokenSource.Cancel();
                _enumerator?.DisposeAsync().AsTask().Wait(TimeSpan.FromSeconds(1));
                _cancellationTokenSource.Dispose();
            }
            base.Dispose(disposing);
        }

        public override async ValueTask DisposeAsync()
        {
            if (!_disposed)
            {
                _disposed = true;
                _cancellationTokenSource.Cancel();
                if (_enumerator != null)
                {
                    await _enumerator.DisposeAsync();
                }
                _cancellationTokenSource.Dispose();
            }
            await base.DisposeAsync();
        }
    }
}