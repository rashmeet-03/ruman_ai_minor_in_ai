
print("Testing imports...")
try:
    import chromadb
    print("✅ chromadb imported")
except ImportError as e:
    print(f"❌ chromadb failed: {e}")

try:
    import mistralai
    print("✅ mistralai imported")
except ImportError as e:
    print(f"❌ mistralai failed: {e}")

try:
    import huggingface_hub
    print(f"✅ huggingface_hub imported (v{huggingface_hub.__version__})")
except ImportError as e:
    print(f"❌ huggingface_hub failed: {e}")

try:
    import transformers
    print(f"✅ transformers imported (v{transformers.__version__})")
except ImportError as e:
    print(f"❌ transformers failed: {e}")

try:
    from sentence_transformers import SentenceTransformer
    print("✅ sentence_transformers imported")
    # Try loading a dummy config to trigger version check
    try:
        from transformers.utils import check_min_version
        check_min_version("4.0.0")
        print("✅ transformers version check passed")
    except Exception as e:
        print(f"❌ transformers version check failed: {e}")

except ImportError as e:
    print(f"❌ sentence_transformers failed: {e}")
except Exception as e:
    print(f"❌ sentence_transformers generic error: {e}")

print("Import test complete.")
