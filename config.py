"""
VideoDistill 配置文件
"""

# Gemini AI 模型配置
DEFAULT_MODEL = "gemini-3-pro-preview"
AVAILABLE_MODELS = [
    "gemini-3-pro-preview",
    "gemini-3-flash-preview"
]

# 笔记生成模式配置
GENERATION_MODES = {
    "segmented": "分段生成（适合长视频）",
    "direct": "直接生成（适合短视频）"
}
DEFAULT_GENERATION_MODE = "direct"

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
