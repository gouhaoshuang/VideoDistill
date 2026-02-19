"""
VideoDistill 配置文件
"""

# Gemini AI 模型配置
DEFAULT_MODEL = "gemini-2.0-flash"
AVAILABLE_MODELS = [
    "gemini-3-pro-preview",
    "gemini-3-flash-preview"
]

# 文件存储配置
TEMP_DIR = "temp"
OUTPUT_DIR = "outputs"
PROMPTS_DIR = "src/prompts"

# API 配置
API_KEY_ENV = "GOOGLE_API_KEY"

# 缓存配置
ENABLE_CACHE = True
CACHE_DIR = "outputs"

# 文件上传配置
MAX_VIDEO_SIZE_MB = 2000
SUPPORTED_VIDEO_FORMATS = ["mp4", "mov", "avi", "mkv", "webm"]
