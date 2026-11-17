"""Run tests without reading any real configuration or accessing the network."""
from pathlib import Path
import os
import sys
import unittest
from unittest.mock import patch

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'backend'))
for name in list(os.environ):
    if name.startswith(('GEMINI_', 'GOOGLE_', 'APIFY_', 'VPS_', 'VIRAL_DNA_')):
        os.environ.pop(name, None)
# Patch before importing the runtime: project .env and external env files are never read.
with patch('dotenv.dotenv_values', return_value={}):
    import local_runtime
    import test_offline
assert local_runtime.PROJECT_ENV == {}
assert not local_runtime.configuration_ready()
assert not local_runtime.EXTERNAL_OPERATIONS_ENABLED
suite = unittest.defaultTestLoader.loadTestsFromModule(test_offline)
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
