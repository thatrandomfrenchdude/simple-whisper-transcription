#!/usr/bin/env python3
"""
Extract mel filters from OpenAI's Whisper model for better transcription quality.
This script downloads the proper mel filters and saves them to mel_filters.npz.
"""

import numpy as np
import os

def extract_mel_filters():
    """Extract mel filters from Whisper and save to mel_filters.npz"""
    
    print("🔄 Loading Whisper model to extract mel filters...")
    
    try:
        import whisper
        
        # Load the base model (you can change to 'small', 'medium', 'large' for different models)
        model = whisper.load_model("base")
        
        print(f"✅ Whisper model loaded successfully")
        print(f"   Model dimensions: {model.dims}")
        
        # Extract the mel filter bank
        mel_filters = model.dims.n_mels
        print(f"   Number of mel filters: {mel_filters}")
        
        # Get the actual mel filter matrix from the model
        # The mel filters are typically stored in the model's preprocessing
        try:
            # Create mel filters using Whisper's built-in function
            import whisper.audio
            mel_filter_matrix = whisper.audio.mel_filters(
                device="cpu",  # Use CPU to get numpy-compatible tensor
                n_mels=80   # Number of mel bands
            )
            
            # Convert to numpy if it's a torch tensor
            if hasattr(mel_filter_matrix, 'numpy'):
                mel_filter_matrix = mel_filter_matrix.numpy()
            elif hasattr(mel_filter_matrix, 'cpu'):
                mel_filter_matrix = mel_filter_matrix.cpu().numpy()
            
            print(f"   Mel filter matrix shape: {mel_filter_matrix.shape}")
            print(f"   Mel filter data type: {mel_filter_matrix.dtype}")
            
            # Save to npz file
            output_path = "mel_filters.npz"
            np.savez(output_path, mel_filters=mel_filter_matrix)
            
            print(f"✅ Mel filters saved to: {os.path.abspath(output_path)}")
            print(f"   File size: {os.path.getsize(output_path)} bytes")
            
            # Verify the saved file
            loaded = np.load(output_path)
            if 'mel_filters' in loaded:
                print(f"✅ Verification: Successfully saved and loaded mel filters")
                print(f"   Loaded shape: {loaded['mel_filters'].shape}")
                loaded.close()
            else:
                print("❌ Error: mel_filters not found in saved file")
                
        except Exception as e:
            print(f"❌ Error extracting mel filters: {e}")
            print("🔄 Trying alternative method...")
            
            # Alternative: Use the audio preprocessing functions directly
            import whisper.audio
            
            # Create mel filters using Whisper's audio processing
            mel_filter_matrix = whisper.audio.mel_filters(
                device="cpu",
                n_mels=80
            )
            
            # Convert to numpy if it's a torch tensor
            if hasattr(mel_filter_matrix, 'numpy'):
                mel_filter_matrix = mel_filter_matrix.numpy()
            elif hasattr(mel_filter_matrix, 'cpu'):
                mel_filter_matrix = mel_filter_matrix.cpu().numpy()
            
            print(f"   Alternative mel filter matrix shape: {mel_filter_matrix.shape}")
            
            # Save to npz file
            output_path = "mel_filters.npz"
            np.savez(output_path, mel_filters=mel_filter_matrix)
            
            print(f"✅ Mel filters saved to: {os.path.abspath(output_path)}")
            
    except Exception as e:
        print(f"❌ Error loading Whisper model: {e}")
        print("Please make sure whisper is installed: pip install openai-whisper")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Whisper Mel Filter Extractor")
    print("=" * 60)
    
    if extract_mel_filters():
        print("\n" + "=" * 60)
        print("SUCCESS: Mel filters extracted successfully!")
        print("=" * 60)
        print("Next steps:")
        print("1. Copy mel_filters.npz to your dist folder for distribution")
        print("2. The updated code will automatically use these improved filters")
        print("3. Rebuild your executable to include the better filters")
    else:
        print("\n" + "=" * 60)
        print("FAILED: Could not extract mel filters")
        print("=" * 60)
        print("The application will continue to use simplified mel filters")
