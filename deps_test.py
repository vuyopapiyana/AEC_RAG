import sys
import platform
import importlib.metadata

def run_checks():
    print("-" * 50)
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("-" * 50)

    # 1. Test Torch (Unpinned)
    print("1. Testing torch import...")
    try:
        import torch
        print(f"   SUCCESS: torch imported successfully.")
        print(f"   Version: {torch.__version__}")
        print(f"   CUDA Available: {torch.cuda.is_available()}")
    except ImportError as e:
        print(f"   FAILURE: Could not import torch: {e}")
        sys.exit(1)

    # 2. Test Docling
    print("\n2. Testing docling import and initialization...")
    try:
        # Check version
        version = importlib.metadata.version("docling")
        print(f"   Found docling version: {version}")
        
        # Try importing specific components to ensure native libs are linked
        from docling.document_converter import DocumentConverter
        
        print("   Initializing DocumentConverter (verifies system dependencies)...")
        converter = DocumentConverter()
        print("   SUCCESS: DocumentConverter initialized.")
        
    except ImportError as e:
        print(f"   FAILURE: Could not import docling: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"   FAILURE: Error initializing docling components: {e}")
        print("   This often indicates missing system dependencies (libmagic, GL, etc).")
        sys.exit(1)

    print("-" * 50)
    print("✅ VERIFICATION SUCCESSFUL: Environment is ready.")
    print("-" * 50)

if __name__ == "__main__":
    run_checks()
