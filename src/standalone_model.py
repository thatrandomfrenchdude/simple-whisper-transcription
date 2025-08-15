# ---------------------------------------------------------------------
# Standalone ONNX model wrapper without AI Hub dependencies
# ---------------------------------------------------------------------
import numpy as np
import onnxruntime
import sys
import os

# Add src directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Handle imports for both direct Python execution and PyInstaller
try:
    from standalone_whisper import StandaloneWhisperApp, TorchNumpyAdapter
except ImportError:
    from .standalone_whisper import StandaloneWhisperApp, TorchNumpyAdapter


def get_onnx_session_with_fallback(path):
    """
    Create ONNX Runtime session with QNN provider fallback to CPU.
    More robust for PyInstaller executables.
    """
    options = onnxruntime.SessionOptions()
    
    # First, try QNN provider (for Snapdragon X Elite optimization)
    try:
        session = onnxruntime.InferenceSession(
            path,
            sess_options=options,
            providers=["QNNExecutionProvider"],
            provider_options=[
                {
                    "backend_path": "QnnHtp.dll",
                    "htp_performance_mode": "burst",
                    "high_power_saver": "sustained_high_performance",
                    "enable_htp_fp16_precision": "1",
                    "htp_graph_finalization_optimization_mode": "3",
                }
            ],
        )
        return session
    except Exception as e:
        # Fall back to CPU provider silently
        pass
    
    # Fall back to CPU provider
    try:
        session = onnxruntime.InferenceSession(
            path,
            sess_options=options,
            providers=["CPUExecutionProvider"],
        )
        return session
    except Exception as e:
        print(f"❌ Failed to load {os.path.basename(path)}: {str(e)}")
        sys.stdout.flush()
        raise e


class StandaloneONNXEncoder:
    """Standalone ONNX encoder wrapper"""
    def __init__(self, encoder_path):
        self.session = get_onnx_session_with_fallback(encoder_path)

    def __call__(self, audio):
        try:
            # Uncomment the line below for debugging
            # print(f"🔍 Encoder input shape: {audio.shape}, dtype: {audio.dtype}")
            # sys.stdout.flush()
            return self.session.run(None, {"audio": audio})
        except Exception as e:
            print(f"❌ Error in encoder inference: {e}")
            print(f"   Input type: {type(audio)}")
            print(f"   Input shape: {getattr(audio, 'shape', 'No shape attr')}")
            print(f"   Input dtype: {getattr(audio, 'dtype', 'No dtype attr')}")
            sys.stdout.flush()
            raise


class StandaloneONNXDecoder:
    """Standalone ONNX decoder wrapper"""
    def __init__(self, decoder_path):
        self.session = get_onnx_session_with_fallback(decoder_path)

    def __call__(self, x, index, k_cache_cross, v_cache_cross, k_cache_self, v_cache_self):
        try:
            # Convert torch tensors to numpy if needed
            if hasattr(index, 'numpy'):
                index_np = index.numpy()
            else:
                index_np = np.array(index)
                
            return self.session.run(
                None,
                {
                    "x": x.astype(np.int32),
                    "index": index_np.astype(np.int32),
                    "k_cache_cross": k_cache_cross,
                    "v_cache_cross": v_cache_cross,
                    "k_cache_self": k_cache_self,
                    "v_cache_self": v_cache_self,
                },
            )
        except Exception as e:
            print(f"❌ Error in decoder inference: {e}")
            sys.stdout.flush()
            raise


class StandaloneWhisperModel:
    """
    Standalone Whisper model that works without AI Hub dependencies.
    Complete replacement for WhisperBaseEnONNX and WhisperApp.
    """
    def __init__(self, encoder_path, decoder_path):
        # Create ONNX model wrappers (use directly, no TorchNumpyAdapter needed)
        self.encoder = StandaloneONNXEncoder(encoder_path)
        self.decoder = StandaloneONNXDecoder(decoder_path)
        
        # Model parameters for Whisper Base EN
        self.num_decoder_blocks = 6
        self.num_decoder_heads = 8
        self.attention_dim = 512

    def transcribe(self, audio: np.ndarray, sample_rate: int) -> str:
        """Transcribe audio to text"""
        try:
            app = StandaloneWhisperApp(
                encoder=self.encoder,
                decoder=self.decoder,
                num_decoder_blocks=self.num_decoder_blocks,
                num_decoder_heads=self.num_decoder_heads,
                attention_dim=self.attention_dim,
            )
            return app.transcribe(audio, sample_rate)
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            sys.stdout.flush()
            return ""
