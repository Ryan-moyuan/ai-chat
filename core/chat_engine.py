"""聊天引擎 - 支持 API 和 Ollama 本地模型"""
import requests
from config_loader import load_config


def _is_ollama():
    config = load_config()
    return config.get("use_ollama", False)


def _get_ollama_url():
    config = load_config()
    return config.get("ollama_url", "http://localhost:11434")


def _get_model():
    config = load_config()
    if _is_ollama():
        return config.get("ollama_model", "qwen2.5:7b")
    return config.get("claude_model", "claude-sonnet-4-20250514")


def chat(messages, system_context=""):
    """发送聊天请求，返回流式生成器"""
    if _is_ollama():
        return _chat_ollama(messages, system_context)
    else:
        return _chat_anthropic(messages, system_context)


def _chat_anthropic(messages, system_context=""):
    """Anthropic API 聊天"""
    from anthropic import Anthropic
    config = load_config()
    api_key = config.get("anthropic_api_key", "")
    if not api_key:
        raise ValueError("请在设置中配置 API Key，或使用本地 Ollama 模型")

    kwargs = {"api_key": api_key}
    base_url = config.get("anthropic_base_url", "")
    if base_url:
        kwargs["base_url"] = base_url

    client = Anthropic(**kwargs)
    model = _get_model()

    req_kwargs = {
        "model": model,
        "messages": messages,
        "max_tokens": 4096,
        "stream": True,
    }
    if system_context:
        req_kwargs["system"] = system_context

    return client.messages.create(**req_kwargs)


def _chat_ollama(messages, system_context=""):
    """Ollama 本地模型聊天"""
    url = f"{_get_ollama_url()}/api/chat"
    model = _get_model()

    # 转换消息格式
    ollama_messages = []
    system_prompt = system_context
    for msg in messages:
        if msg["role"] == "user":
            ollama_messages.append({"role": "user", "content": msg["content"]})
        else:
            ollama_messages.append({"role": "assistant", "content": msg["content"]})

    body = {
        "model": model,
        "messages": ollama_messages,
        "stream": True,
    }
    if system_prompt:
        # Ollama system prompt 放在第一条
        ollama_messages.insert(0, {"role": "system", "content": system_prompt})
        body["messages"] = ollama_messages

    # 流式响应 - 返回一个生成器
    response = requests.post(url, json=body, stream=True)
    response.raise_for_status()

    return OllamaStream(response)


class OllamaStream:
    """Ollama 流式响应包装器"""
    def __init__(self, response):
        self.response = response

    def __iter__(self):
        for line in self.response.iter_lines():
            if line:
                import json
                data = json.loads(line)
                if "message" in data and "content" in data["message"]:
                    yield ChatChunk(data["message"]["content"])
                if data.get("done", False):
                    break


class ChatChunk:
    """模拟 Anthropic 的 chunk 对象"""
    def __init__(self, text):
        self.delta = ChunkDelta(text)


class ChunkDelta:
    def __init__(self, text):
        self.text = text


def _extract_text(response):
    """提取文本内容，过滤 thinking block"""
    texts = []
    for block in response.content:
        if hasattr(block, 'type') and block.type == 'text':
            texts.append(block.text)
        elif hasattr(block, 'type') and block.type == 'thinking':
            pass  # skip thinking blocks
        else:
            text = getattr(block, 'text', None)
            if text:
                texts.append(text)
    return "".join(texts)


def chat_full(messages, system_context=""):
    """非流式，返回完整文本"""
    if _is_ollama():
        # Ollama 非流式
        url = f"{_get_ollama_url()}/api/chat"
        model = _get_model()
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({"role": msg["role"], "content": msg["content"]})
        if system_context:
            ollama_messages.insert(0, {"role": "system", "content": system_context})

        body = {"model": model, "messages": ollama_messages, "stream": False}
        response = requests.post(url, json=body)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]
    else:
        from anthropic import Anthropic
        config = load_config()
        api_key = config.get("anthropic_api_key", "")
        if not api_key:
            raise ValueError("请在设置中配置 API Key")

        kwargs = {"api_key": api_key}
        base_url = config.get("anthropic_base_url", "")
        if base_url:
            kwargs["base_url"] = base_url

        client = Anthropic(**kwargs)
        model = _get_model()

        req_kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": 4096,
        }
        if system_context:
            req_kwargs["system"] = system_context

        response = client.messages.create(**req_kwargs)
        return _extract_text(response)
