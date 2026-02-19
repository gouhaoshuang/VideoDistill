"""
Gemini API 客户端封装

负责与 Gemini AI API 的交互，包括文件上传、内容生成等。
"""

import os
import time
from typing import Optional, List
from google import genai
from google.genai import types


class GeminiClient:
    """Gemini AI API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            api_key: Gemini API Key，如果不提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("请提供 GOOGLE_API_KEY")

        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash"

    def upload_video(self, video_path: str, wait_for_ready: bool = True, timeout: int = 300):
        """
        上传视频文件到 Gemini Files API

        Args:
            video_path: 视频文件路径
            wait_for_ready: 是否等待文件处理完成
            timeout: 等待超时时间（秒）

        Returns:
            上传的文件对象
        """
        print(f"正在上传视频: {video_path}")
        file = self.client.files.upload(file=video_path)
        print(f"文件已上传: {file.name}")

        if wait_for_ready:
            print("等待文件处理完成...")
            file = self.wait_for_file_ready(file.name, timeout)

        return file

    def wait_for_file_ready(self, file_name: str, timeout: int = 300):
        """
        等待文件处理完成（ACTIVE 状态）

        Args:
            file_name: 文件名
            timeout: 超时时间（秒）

        Returns:
            处理完成的文件对象

        Raises:
            TimeoutError: 如果文件在超时时间内未变为 ACTIVE 状态
        """
        start_time = time.time()
        check_interval = 2  # 每2秒检查一次

        while time.time() - start_time < timeout:
            try:
                file = self.client.files.get(name=file_name)
                print(f"  文件状态: {file.state}")

                if file.state == "ACTIVE":
                    print("文件已就绪！")
                    return file
                elif file.state in ["FAILED", "ERROR"]:
                    raise Exception(f"文件处理失败: {file.state}")

                time.sleep(check_interval)
            except Exception as e:
                print(f"  检查文件状态出错: {e}")
                time.sleep(check_interval)

        raise TimeoutError(f"文件在 {timeout} 秒内未处理完成")

    def upload_file(self, file_path: str):
        """
        上传任意文件到 Gemini Files API

        Args:
            file_path: 文件路径

        Returns:
            上传的文件对象
        """
        print(f"正在上传文件: {file_path}")
        return self.client.files.upload(file=file_path)

    def generate_content(
        self,
        prompt: str,
        file=None,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 5
    ) -> str:
        """
        生成内容（带自动重试）

        Args:
            prompt: 提示词
            file: 可选的文件对象
            system_instruction: 系统指令
            temperature: 温度参数 (0-1)
            max_retries: 最大重试次数

        Returns:
            生成的文本内容
        """
        contents = [prompt]
        if file:
            contents.append(file)

        config = types.GenerateContentConfig(
            temperature=temperature,
        )

        if system_instruction:
            config.system_instruction = system_instruction

        # 重试逻辑：处理 429 速率限制错误
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config
                )
                return response.text

            except Exception as e:
                error_str = str(e)
                # 检查是否是速率限制错误
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    if attempt < max_retries - 1:
                        # 指数退避：2^attempt 秒
                        wait_time = min(2 ** attempt, 60)  # 最多等待 60 秒
                        print(f"  遇到速率限制，等待 {wait_time} 秒后重试... (尝试 {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"达到最大重试次数，请求失败: {error_str}")
                else:
                    # 其他错误直接抛出
                    raise

    def generate_content_stream(
        self,
        prompt: str,
        file=None,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        流式生成内容

        Args:
            prompt: 提示词
            file: 可选的文件对象
            system_instruction: 系统指令
            temperature: 温度参数 (0-1)

        Yields:
            生成的文本块
        """
        contents = [prompt]
        if file:
            contents.append(file)

        config = types.GenerateContentConfig(
            temperature=temperature,
        )

        if system_instruction:
            config.system_instruction = system_instruction

        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=config
        ):
            yield chunk.text

    def delete_file(self, file_name: str):
        """
        删除上传的文件

        Args:
            file_name: 文件名
        """
        try:
            self.client.files.delete(name=file_name)
            print(f"已删除文件: {file_name}")
        except Exception as e:
            print(f"删除文件失败: {e}")

    def list_files(self) -> List:
        """
        列出所有已上传的文件

        Returns:
            文件列表
        """
        return list(self.client.files.list())
