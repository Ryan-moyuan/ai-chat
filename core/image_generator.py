"""图像生成引擎 - 本地 Stable Diffusion + API 双模式"""
import os
import base64
import requests
from PIL import Image
from io import BytesIO
from config_loader import load_config, IMAGES_DIR


def generate_local(prompt, negative_prompt="", num_steps=30, width=512, height=512):
    """使用本地 Stable Diffusion 生成图像"""
    config = load_config()
    model_name = config.get("sd_model", "runwayml/stable-diffusion-v1-5")

    try:
        from diffusers import StableDiffusionPipeline
        import torch
    except ImportError:
        raise ImportError("请先安装 diffusers 和 torch: pip install diffusers torch torchvision")

    pipe = StableDiffusionPipeline.from_pretrained(model_name)
    pipe = pipe.to("mps" if torch.backends.mps.is_available() else "cpu")

    generator = None
    if hasattr(torch, "mps"):
        generator = torch.Generator("mps" if torch.backends.mps.is_available() else "cpu")
        generator.manual_seed(42)

    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt if negative_prompt else None,
        num_inference_steps=num_steps,
        width=width,
        height=height,
        generator=generator,
    )
    return result.images[0]


def generate_api_dalle(prompt, negative_prompt="", num_steps=30, width=512, height=512):
    """使用 DALL-E API 生成图像"""
    from openai import OpenAI
    config = load_config()
    api_key = config.get("openai_api_key", "")
    if not api_key:
        raise ValueError("请在设置中配置 OpenAI API Key")

    client = OpenAI(api_key=api_key)
    size_map = {
        (512, 512): "512x512",
        (256, 256): "256x256",
        (1024, 1024): "1024x1024",
        (1024, 1792): "1024x1792",
        (1792, 1024): "1792x1024",
    }
    size = size_map.get((width, height), "1024x1024")

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        n=1,
    )
    img_url = response.data[0].url
    img_resp = requests.get(img_url)
    return Image.open(BytesIO(img_resp.content))


def generate_api_stability(prompt, negative_prompt="", num_steps=30, width=512, height=512):
    """使用 Stability AI API 生成图像"""
    config = load_config()
    api_key = config.get("stability_api_key", "")
    if not api_key:
        raise ValueError("请在设置中配置 Stability AI API Key")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "image/png",
    }
    body = {
        "prompt": prompt,
        "negative_prompt": negative_prompt or "",
        "steps": num_steps,
        "width": width,
        "height": height,
    }

    resp = requests.post(
        "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
        headers=headers,
        json=body,
    )
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content))


def generate(prompt, mode="local", **kwargs):
    """
    生成图像
    mode: "local" | "dalle" | "stability"
    kwargs: negative_prompt, num_steps, width, height
    """
    generators = {
        "local": generate_local,
        "dalle": generate_api_dalle,
        "stability": generate_api_stability,
    }
    func = generators.get(mode, generate_local)
    return func(prompt, **kwargs)


def save_image(image, filename=None):
    """保存图像到 data/generated_images/"""
    if filename is None:
        from datetime import datetime
        filename = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    path = os.path.join(IMAGES_DIR, filename)
    image.save(path)
    return path
