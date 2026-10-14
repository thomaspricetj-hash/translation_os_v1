import subprocess
import sys
import os
import argparse
from pathlib import Path

def get_python_executable():
    """Get the Python executable - prioritize weave-train env."""
    # Check if we're in weave-train or use the conda env directly
    weave_train_python = "C:/ProgramData/Miniconda3/envs/weave-train/python.exe"
    if os.path.exists(weave_train_python):
        print(f"[INFO] Using weave-train environment Python: {weave_train_python}")
        return weave_train_python
    
    # Fallback to current python
    return sys.executable

def run_command(command, description):
    """Helper to run a shell command and report status."""
    print(f"\n[STARTING] {description}...")
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, text=True)
        print(f"[SUCCESS] {description} completed.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred during {description}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Automate WeaveFormer Training and GGUF Conversion")
    parser.add_argument("--config", type=str, required=True, help="Path to the HF config file (e.g., weaveformer/config-5b.json)")
    parser.add_argument("--model_name", type=str, required=True, help="Base name for output files (e.g., 'weave-5b')")
    parser.add_argument("--output_dir", type=str, default="models", help="Directory to save the HF model and GGUF file")
    parser.add_argument("--quantize", action="store_true", default=False, help="Whether to apply quantization during conversion")
    
    args = parser.parse_args()

    workspace_root = Path(os.getcwd())
    train_script = workspace_root / "weaveformer" / "train_weaveformer.py"
    convert_script = workspace_root / "weaveformer" / "convert_hf_to_gguf.py"
    config_path = workspace_root / args.config
    
    hf_output_dir = workspace_root / args.output_dir / f"{args.model_name}-hf"
    gguf_output_file = workspace_root / args.output_dir / f"{args.model_name}.gguf"

    if not config_path.exists():
        print(f"[FATAL] Configuration file not found: {config_path}")
        sys.exit(1)

    # Get the correct Python executable
    python_executable = get_python_executable()

    # Training
    train_cmd = [python_executable, str(train_script), "--config", str(config_path), "--output", str(hf_output_dir)]
    
    if not run_command(train_cmd, f"Training WeaveFormer ({args.model_name})"):
        print("[ABORTING] Training stage failed.")
        sys.exit(1)

    # Conversion to GGUF
    convert_cmd = [python_executable, str(convert_script), "--model-path", str(hf_output_dir), "--outfile", str(gguf_output_file)]
    
    if args.quantize:
        convert_cmd.append("--quantize")

    if not run_command(convert_cmd, f"Converting to GGUF ({gguf_output_file.name})"):
        print("[ABORTING] Conversion stage failed.")
        sys.exit(1)

    print("\n" + "="*50)
    print("PIPELINE COMPLETE SUCCESSFULLY!")
    print(f"HF Model: {hf_output_dir}")
    print(f"GGUF Model: {gguf_output_file}")
    print("="*50)

if __name__ == "__main__":
    main()
