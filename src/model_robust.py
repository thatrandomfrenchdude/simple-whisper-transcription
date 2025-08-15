# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
import numpy as np
import onnxruntime
import sys
import os
from qai_hub_models.models._shared.whisper.model import Whisper


def get_onnxruntime_session_with_fallback(path):
    """
    Try to create an ONNX Runtime session with QNN provider first,
    then fall back to CPU provider if QNN is not available.
    This is more robust for PyInstaller executables.
    """
    options = onnxruntime.SessionOptions()
    
    # First, try QNN provider (for Snapdragon X Elite optimization)
    try:
        print(f"Attempting to load {os.path.basename(path)} with QNN provider...")
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
        print(f"✓ Successfully loaded {os.path.basename(path)} with QNN provider")
        return session
    except Exception as e:
        print(f"⚠ QNN provider failed for {os.path.basename(path)}: {str(e)}")
        print("Falling back to CPU provider...")
    
    # Fall back to CPU provider
    try:
        session = onnxruntime.InferenceSession(
            path,
            sess_options=options,
            providers=["CPUExecutionProvider"],
        )
        print(f"✓ Successfully loaded {os.path.basename(path)} with CPU provider")
        return session
    except Exception as e:
        print(f"✗ Failed to load {os.path.basename(path)} with CPU provider: {str(e)}")
        raise e


def get_onnxruntime_session_with_qnn_ep(path):
    """Original function - kept for compatibility but now uses fallback"""
    return get_onnxruntime_session_with_fallback(path)


class ONNXEncoderWrapper:
    def __init__(self, encoder_path):
        print("Initializing ONNX Encoder...")
        self.session = get_onnxruntime_session_with_fallback(encoder_path)

    def to(self, *args):
        return self

    def __call__(self, audio):
        try:
            return self.session.run(None, {"audio": audio})
        except Exception as e:
            print(f"Error in encoder inference: {e}")
            raise


class ONNXDecoderWrapper:
    def __init__(self, decoder_path):
        print("Initializing ONNX Decoder...")
        self.session = get_onnxruntime_session_with_fallback(decoder_path)

    def to(self, *args):
        return self

    def __call__(
        self, x, index, k_cache_cross, v_cache_cross, k_cache_self, v_cache_self
    ):
        try:
            return self.session.run(
                None,
                {
                    "x": x.astype(np.int32),
                    "index": np.array(index),
                    "k_cache_cross": k_cache_cross,
                    "v_cache_cross": v_cache_cross,
                    "k_cache_self": k_cache_self,
                    "v_cache_self": v_cache_self,
                },
            )
        except Exception as e:
            print(f"Error in decoder inference: {e}")
            raise


class WhisperBaseEnONNX(Whisper):
    def __init__(self, encoder_path, decoder_path):
        print("Initializing Whisper Base EN ONNX model...")
        return super().__init__(
            ONNXEncoderWrapper(encoder_path),
            ONNXDecoderWrapper(decoder_path),
            num_decoder_blocks=6,
            num_heads=8,
            attention_dim=512,
        )
