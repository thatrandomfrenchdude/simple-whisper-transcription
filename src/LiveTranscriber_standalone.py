import numpy as np
import os
import queue
import sounddevice as sd
import sys
import threading
import yaml
import traceback

from concurrent.futures import ThreadPoolExecutor

# Add src directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Handle imports for both direct Python execution and PyInstaller
try:
    from standalone_model import StandaloneWhisperModel
except ImportError:
    from .standalone_model import StandaloneWhisperModel


def flush_output():
    """Force flush stdout and stderr for better console output in executables"""
    sys.stdout.flush()
    sys.stderr.flush()


def process_transcription(
    whisper_model: StandaloneWhisperModel,
    chunk: np.ndarray,
    silence_threshold: float,
    sample_rate: int
) -> None:
    """
    Process a chunk of audio data and transcribe it using the Whisper model.
    This function is run in a separate thread to allow for concurrent processing.
    """
    
    try:
        if np.abs(chunk).mean() > silence_threshold:
            transcript = whisper_model.transcribe(chunk, sample_rate)
            if transcript.strip():
                print(f"Transcript: {transcript}")
                flush_output()
    except Exception as e:
        print(f"❌ Error in transcription: {e}")
        traceback.print_exc()
        flush_output()


def process_audio(
    whisper_model: StandaloneWhisperModel,
    audio_queue: queue.Queue,
    stop_event: threading.Event,
    max_workers: int,
    queue_timeout: float,
    chunk_samples: int,
    silence_threshold: float,
    sample_rate: int
) -> None:
    """
    Process audio data from the queue and transcribe it using the Whisper model.
    """

    buffer = np.empty((0,), dtype=np.float32)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        
        while not stop_event.is_set():
            try:
                audio_chunk = audio_queue.get(timeout=queue_timeout)
                audio_chunk = audio_chunk.flatten()
                buffer = np.concatenate([buffer, audio_chunk])

                while len(buffer) >= chunk_samples:
                    current_chunk = buffer[:chunk_samples]
                    buffer = buffer[chunk_samples:]
                    
                    future = executor.submit(
                        process_transcription,
                        whisper_model,
                        current_chunk,
                        silence_threshold,
                        sample_rate
                    )
                    futures = [f for f in futures if not f.done()] + [future]

            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error in audio processing: {e}")
                traceback.print_exc()
                flush_output()
            
        # Wait for transcription futures to complete
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"❌ Error in future result: {e}")
                flush_output()


def record_audio(
    audio_queue: queue.Queue,
    stop_event: threading.Event,
    sample_rate: int,
    channels: int
) -> None:
    """
    Record audio from the microphone and put it into the audio queue.
    """

    def audio_callback(indata, frames, time, status):
        """Callback function for audio input stream."""
        if not stop_event.is_set():
            audio_queue.put(indata.copy())

    try:        
        with sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            callback=audio_callback
        ):
            print("✅ Microphone stream initialized... (Press Ctrl+C to stop)")
            print("=" * 50)
            flush_output()
            stop_event.wait()
    except Exception as e:
        print(f"❌ Error in audio recording: {e}")
        traceback.print_exc()
        flush_output()


class StandaloneLiveTranscriber:
    def __init__(self):
        print("🚀 Starting Standalone Whisper Transcription")
        flush_output()
        
        try:
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
            
            print("✅ Configuration loaded successfully")
            flush_output()
            
            # audio settings
            self.sample_rate = config.get("sample_rate", 16000)
            self.chunk_duration = config.get("chunk_duration", 4)
            self.channels = config.get("channels", 1)
            
            # processing settings
            self.max_workers = config.get("max_workers", 4)
            self.silence_threshold = config.get("silence_threshold", 0.001)
            self.queue_timeout = config.get("queue_timeout", 1.0)
            self.chunk_samples = int(self.sample_rate * self.chunk_duration)
            
            # model paths
            self.encoder_path = config.get("encoder_path", "models/WhisperEncoder.onnx")
            self.decoder_path = config.get("decoder_path", "models/WhisperDecoder.onnx")

            # check that the model paths exist
            if not os.path.exists(self.encoder_path):
                print(f"❌ Encoder model not found at {self.encoder_path}")
                flush_output()
                sys.exit(f"Encoder model not found at {self.encoder_path}.")
                
            if not os.path.exists(self.decoder_path):
                print(f"❌ Decoder model not found at {self.decoder_path}")
                flush_output()
                sys.exit(f"Decoder model not found at {self.decoder_path}.")

            print("✅ Model files found")
            flush_output()

            # initialize the model
            print("🤖 Loading Standalone Whisper model...")
            flush_output()
            
            self.model = StandaloneWhisperModel(self.encoder_path, self.decoder_path)
            
            print("✅ Model loaded successfully!")
            flush_output()

            # initialize the audio queue and stop event
            self.audio_queue = queue.Queue()
            self.stop_event = threading.Event()
            
        except Exception as e:
            print(f"❌ Error during initialization: {e}")
            traceback.print_exc()
            flush_output()
            sys.exit(1)

    def run(self):
        """Run the live transcription."""
        
        try:
            # launch the audio processing and recording threads
            process_thread = threading.Thread(
                target=process_audio, 
                args=(
                    self.model,
                    self.audio_queue,
                    self.stop_event,
                    self.max_workers,
                    self.queue_timeout,
                    self.chunk_samples,
                    self.silence_threshold,
                    self.sample_rate
                )
            )
            process_thread.start()

            record_thread = threading.Thread(
                target=record_audio, 
                args=(
                    self.audio_queue,
                    self.stop_event,
                    self.sample_rate,
                    self.channels
                )
            )
            record_thread.start()

            # wait for threads to finish
            try:
                while True:
                    record_thread.join(timeout=0.1)
                    if not record_thread.is_alive():
                        break
            except KeyboardInterrupt:
                print("\nStopping transcription...")
                flush_output()
            finally:
                self.stop_event.set()
                record_thread.join()
                process_thread.join()
                
        except Exception as e:
            print(f"❌ Error during execution: {e}")
            traceback.print_exc()
            flush_output()


if __name__ == "__main__":
    transcriber = StandaloneLiveTranscriber()
    transcriber.run()
