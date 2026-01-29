# File: bridge/stream_buffer.py
import collections

class AudioStreamBuffer:
    def __init__(self, window_seconds=2.0, sample_rate=16000, stride_ms=320):
        self.sample_rate = sample_rate
        self.bytes_per_sample = 2  # PCM16
        self.window_size = int(window_seconds * sample_rate * self.bytes_per_sample)
        self.stride_size = int((stride_ms / 1000.0) * sample_rate * self.bytes_per_sample)
        
        self.buffer = bytearray()
        self.bytes_since_last_search = 0

    def append_and_check(self, chunk: bytes):
        """
        Adds new audio to the buffer and returns (True, window) 
        if we've crossed the stride threshold.
        """
        self.buffer.extend(chunk)
        self.bytes_since_last_search += len(chunk)

        # Maintain sliding window size
        if len(self.buffer) > self.window_size:
            self.buffer = self.buffer[-self.window_size:]

        # Trigger search every 'stride_ms'
        if self.bytes_since_last_search >= self.stride_size:
            self.bytes_since_last_search = 0
            # Return a copy of the current 2s window for processing
            return True, bytes(self.buffer)
        
        return False, None