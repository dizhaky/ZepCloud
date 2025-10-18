#!/usr/bin/env python3
"""
Import Standards for Azure RAG Setup
Standardized import order and patterns for all Python files
"""

# Standard import order:
# 1. Standard library imports
# 2. Third-party imports
# 3. Local application imports

# 1. Standard library imports (alphabetical)
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# 2. Third-party imports (alphabetical)
import requests
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm

# 3. Local application imports (alphabetical)
from config_manager import get_config_manager
from logger import setup_logging
from m365_auth import M365Auth

# Example usage in a file:
"""
#!/usr/bin/env python3
\"\"\"
[Module docstring]
\"\"\"

# Standard library imports
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Third-party imports
import requests
from azure.storage.blob import BlobServiceClient
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm

# Local application imports
from config_manager import get_config_manager
from logger import setup_logging
from m365_auth import M365Auth
"""
