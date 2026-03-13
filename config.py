import os

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "").strip()

if not NVIDIA_API_KEY:
    _key_file = os.path.join(os.path.dirname(__file__), "api_keys.txt")
    if os.path.exists(_key_file):
        with open(_key_file) as f:
            NVIDIA_API_KEY = f.read().strip()

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

# NVIDIA NIM basic models
LLM_MODEL = "meta/llama-3.1-8b-instruct"
EMBEDDING_MODEL = "nvidia/nv-embedqa-e5-v5"
EMBEDDING_DIMENSION = 1024

# Lara Translate credentials
LARA_ACCESS_KEY_ID = "5LTVO8QILKTTC3IR262O55SPKD"
LARA_ACCESS_KEY_SECRET = "-Z52NwU3mPw2mthPZWdPoH5P-UMi31d0FPtXti1cLfM"

# Domain categories for customer message classification
DOMAIN_CATEGORIES = [
    "Task",           # General work item
    "Bug",            # Defect / error
    "Enhancement",    # Feature extension
    "Research",       # Investigation / feasibility
    "Design",         # UI/UX / mockup
    "Testing",        # QA / validation
    "Deployment",     # Release / infra / CI-CD
    "Documentation",  # Docs / guide
]
