import os
import sys
from unittest.mock import patch, MagicMock

# Add current directory to path to import app
sys.path.append(os.getcwd())

from app.services.orchestration.metagpt_executor import MetaGPTExecutor
from app.core.exceptions import MetaGPTException

def test_metagpt_executor_config():
    print("Testing MetaGPTExecutor configuration logic...")

    # Case 1: No keys
    with patch('app.services.orchestration.metagpt_executor.settings') as mock_settings:
        mock_settings.OPENAI_API_KEY = ""
        mock_settings.ANTHROPIC_API_KEY = ""
        mock_settings.METAGPT_WORKSPACE = "./workspace"

        executor = MetaGPTExecutor()
        print(f"No keys: metagpt_configured = {executor.metagpt_configured}")
        assert executor.metagpt_configured is False
        assert "MetaGPT requires OPENAI_API_KEY or ANTHROPIC_API_KEY" in executor._setup_error

    # Case 2: OpenAI key
    with patch('app.services.orchestration.metagpt_executor.settings') as mock_settings:
        mock_settings.OPENAI_API_KEY = "sk-1234567890abcdef1234567890abcdef"
        mock_settings.ANTHROPIC_API_KEY = ""
        mock_settings.METAGPT_WORKSPACE = "./workspace"

        with patch('app.services.orchestration.metagpt_executor.yaml.dump') as mock_dump:
            with patch('app.services.orchestration.metagpt_executor.open', MagicMock()):
                with patch('app.services.orchestration.metagpt_executor.Path.mkdir', MagicMock()):
                    executor = MetaGPTExecutor()
                    print(f"OpenAI key: metagpt_configured = {executor.metagpt_configured}")
                    assert executor.metagpt_configured is True
                    assert executor._setup_error is None

    # Case 3: Anthropic key
    with patch('app.services.orchestration.metagpt_executor.settings') as mock_settings:
        mock_settings.OPENAI_API_KEY = ""
        mock_settings.ANTHROPIC_API_KEY = "sk-ant-1234567890abcdef1234567890abcdef"
        mock_settings.METAGPT_WORKSPACE = "./workspace"

        with patch('app.services.orchestration.metagpt_executor.yaml.dump') as mock_dump:
            with patch('app.services.orchestration.metagpt_executor.open', MagicMock()):
                with patch('app.services.orchestration.metagpt_executor.Path.mkdir', MagicMock()):
                    executor = MetaGPTExecutor()
                    print(f"Anthropic key: metagpt_configured = {executor.metagpt_configured}")
                    assert executor.metagpt_configured is True
                    assert executor._setup_error is None

    print("All MetaGPTExecutor configuration logic tests passed!")

if __name__ == "__main__":
    try:
        test_metagpt_executor_config()
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
