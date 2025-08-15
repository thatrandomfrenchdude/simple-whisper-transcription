import numpy as np
import os
import queue
import sounddevice as sd
import sys
import threading
import yaml
import traceback

from concurrent.futures import ThreadPoolExecutor
from model_robust import WhisperBaseEnONNX
from qai_hub_models.models.whisper_base_en import App as WhisperApp


def flush_output():
    """Force flush stdout and stderr for better console output in executables"""
    sys.stdout.flush()
    sys.stderr.flush()


def process_transcription(
    whisper: WhisperApp,
    chunk: np.ndarray,
    silence_threshold: float,
    sample_rate: int
) -> None:
    """
    Process a chunk of audio data and transcribe it using the Whisper model.
    This function is run in a separate thread to allow for concurrent processing.

    Inputs:
    - whisper: WhisperApp instance for transcription
    - chunk: Audio data chunk to be transcribed (numpy array)
    - silence_threshold: Threshold for silence detection
    - sample_rate: Sample rate for audio recording
    """
    
    try:
        if np.abs(chunk).mean() > silence_threshold:
            print(f"🎤 Processing audio chunk (mean amplitude: {np.abs(chunk).mean():.6f})")
            flush_output()
            transcript = whisper.transcribe(chunk, sample_rate)
            if transcript.strip():
                print(f"📝 Transcript: {transcript}")
                flush_output()
    except Exception as e:
        print(f"❌ Error in transcription: {e}")
        traceback.print_exc()
        flush_output()


def process_audio(
    whisper: WhisperApp,
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
    This function runs in a separate thread to allow for concurrent processing.

    Inputs:
    - whisper: WhisperApp instance for transcription
    - audio_queue: Queue containing audio data chunks
    - stop_event: Event to signal when to stop processing
    - max_workers: Number of parallel transcription workers
    - queue_timeout: Timeout for queue operations
    - chunk_samples: Number of samples in each audio chunk
    - silence_threshold: Threshold for silence detection
    - sample_rate: Sample rate for audio recording
    """

    buffer = np.empty((0,), dtype=np.float32)
    print(f"🔄 Audio processing thread started (chunk_samples: {chunk_samples})")
    flush_output()
    
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
                        whisper,
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
            
        print("🔄 Waiting for transcription futures to complete...")
        flush_output()
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
    This function runs in a separate thread to allow for concurrent processing.

    Inputs:
    - audio_queue: Queue to store audio data chunks
    - stop_event: Event to signal when to stop recording
    - sample_rate: Sample rate for audio recording
    - channels: Number of audio channels (1 for mono)
    """

    def audio_callback(indata, frames, time, status):
        """
        Callback function for audio input stream. This function is called by the sounddevice library
        whenever there is new audio data available.
        """

        if status:
            print(f"🔊 Audio Status: {status}")
            flush_output()
        if not stop_event.is_set():
            audio_queue.put(indata.copy())

    try:
        print(f"🎙️ Initializing audio input (sample_rate: {sample_rate}, channels: {channels})")
        flush_output()
        
        with sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            callback=audio_callback
        ):
            print("✅ Microphone stream initialized... (Press Ctrl+C to stop)")
            flush_output()
            stop_event.wait()
    except Exception as e:
        print(f"❌ Error in audio recording: {e}")
        traceback.print_exc()
        flush_output()


class LiveTranscriber:
    def __init__(self):
        print("🚀 Starting Simple Whisper Transcription")
        print("=" * 50)
        flush_output()
        
        try:
            print("📁 Loading configuration file...")
            flush_output()
            
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

            print(f"📊 Audio Settings:")
            print(f"   Sample Rate: {self.sample_rate} Hz")
            print(f"   Chunk Duration: {self.chunk_duration} seconds")
            print(f"   Channels: {self.channels}")
            print(f"   Chunk Samples: {self.chunk_samples}")
            print(f"🔧 Processing Settings:")
            print(f"   Max Workers: {self.max_workers}")
            print(f"   Silence Threshold: {self.silence_threshold}")
            print(f"📁 Model Paths:")
            print(f"   Encoder: {self.encoder_path}")
            print(f"   Decoder: {self.decoder_path}")
            flush_output()

            # check that the model paths exist
            print("🔍 Checking model files...")
            flush_output()
            
            if not os.path.exists(self.encoder_path):
                print(f"❌ Encoder model not found at {self.encoder_path}")
                print(f"Current working directory: {os.getcwd()}")
                print(f"Files in current directory: {os.listdir('.')}")
                if os.path.exists('models'):
                    print(f"Files in models directory: {os.listdir('models')}")
                flush_output()
                sys.exit(f"Encoder model not found at {self.encoder_path}.")
                
            if not os.path.exists(self.decoder_path):
                print(f"❌ Decoder model not found at {self.decoder_path}")
                print(f"Current working directory: {os.getcwd()}")
                print(f"Files in current directory: {os.listdir('.')}")
                if os.path.exists('models'):
                    print(f"Files in models directory: {os.listdir('models')}")
                flush_output()
                sys.exit(f"Decoder model not found at {self.decoder_path}.")

            print("✅ Model files found")
            flush_output()

            # initialize the model
            print("🤖 Loading Whisper model...")
            flush_output()
            
            self.model = WhisperApp(WhisperBaseEnONNX(self.encoder_path, self.decoder_path))
            
            print("✅ Model loaded successfully!")
            flush_output()

            # initialize the audio queue and stop event
            self.audio_queue = queue.Queue()
            self.stop_event = threading.Event()
            
            print("🎯 Initialization complete!")
            print("=" * 50)
            flush_output()
            
        except Exception as e:
            print(f"❌ Error during initialization: {e}")
            traceback.print_exc()
            flush_output()
            sys.exit(1)

    def run(self):
        """
        Run the live transcription.
        """
        
        try:
            print("🎬 Starting transcription threads...")
            flush_output()
            
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
                print("\n🛑 Stopping transcription...")
                flush_output()
            finally:
                self.stop_event.set()
                record_thread.join()
                process_thread.join()
                print("✅ Transcription stopped.")
                flush_output()
                
        except Exception as e:
            print(f"❌ Error during execution: {e}")
            traceback.print_exc()
            flush_output()


if __name__ == "__main__":
    transcriber = LiveTranscriber()
    transcriber.run()
