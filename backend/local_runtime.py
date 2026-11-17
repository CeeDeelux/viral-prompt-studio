"""Provider configuration and explicit session-only online mode."""
import os
from pathlib import Path
import hashlib
from dotenv import dotenv_values
from google import genai
from google.genai import types

# Each backend restart begins offline; enabling a session never performs a provider call.
EXTERNAL_OPERATIONS_ENABLED = False
ALIASES = {'gemini': ('GEMINI_API_KEY', 'GOOGLE_API_KEY', 'GOOGLE_GENERATIVE_AI_API_KEY'),
           'apify': ('APIFY_API_KEY', 'APIFY_API_TOKEN', 'APIFY_TOKEN')}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ENV_PATH = PROJECT_ROOT / '.env'
PROJECT_ENV = dotenv_values(PROJECT_ENV_PATH, interpolate=False, encoding='utf-8-sig') if PROJECT_ENV_PATH.is_file() else {}

def setting(name, default=''):
    return os.environ.get(name, PROJECT_ENV.get(name) or default)

PORT = int(setting('VPS_PORT', '3100'))
if not 1 <= PORT <= 65535:
    raise ValueError('VPS_PORT must be between 1 and 65535')
INSTANCE = hashlib.sha256(str(PROJECT_ROOT).encode()).hexdigest()[:16]
DATA_DIR = PROJECT_ROOT / '.runtime'
ORIGINS = [f'http://127.0.0.1:{PORT}', f'http://localhost:{PORT}']
DEV_PORT = setting('VPS_DEV_PORT')
if DEV_PORT and DEV_PORT.isdigit():
    ORIGINS += [f'http://127.0.0.1:{int(DEV_PORT)}', f'http://localhost:{int(DEV_PORT)}']


def provider_key(provider):
    for name in ALIASES[provider]:
        value = os.environ.get(name, '').strip()
        if value:
            return value
    source = os.environ.get('VPS_' + provider.upper() + '_ENV_FILE')
    values = dotenv_values(Path(source).resolve(), interpolate=False, encoding='utf-8-sig') if source else PROJECT_ENV
    for name in ALIASES[provider]:
        value = (values.get(name) or '').strip()
        if value and not value.lower().startswith(('your_', 'placeholder', 'changeme')):
            return value
    return ''

def configuration_ready():
    return all(bool(provider_key(p)) for p in ALIASES)

def set_mode(mode):
    global EXTERNAL_OPERATIONS_ENABLED
    if mode not in ('offline', 'online'):
        raise ValueError('Mode must be offline or online')
    if mode == 'online' and not configuration_ready():
        raise ValueError('Both Gemini and Apify keys must be configured before enabling online mode')
    EXTERNAL_OPERATIONS_ENABLED = mode == 'online'


def require_external():
    if not EXTERNAL_OPERATIONS_ENABLED:
        raise PermissionError('External operations are blocked in offline mode.')

def generate_text(instruction, content):
    require_external()
    key = provider_key('gemini')
    if not key:
        raise ValueError('Gemini key is missing')
    # Model availability must be checked before future online activation, without auto-fallback.
    model = setting('VPS_GEMINI_MODEL', 'gemini-3-flash-preview')
    with genai.Client(api_key=key, http_options=types.HttpOptions(timeout=120000)) as client:
        response = client.models.generate_content(model=model, contents=content,
            config=types.GenerateContentConfig(system_instruction=instruction,
                temperature=1.0, max_output_tokens=8192))
        if not response.text:
            raise ValueError('Gemini returned no text')
        return response.text
