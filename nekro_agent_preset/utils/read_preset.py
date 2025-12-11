import os
import toml
import base64
from typing import Type, Callable, Any, Dict
from nekro_agent_preset.entity.preset import Preset
from nekro_agent_preset.config import config

def default_handle_for_read_preset(preset_data: Dict[str, Any]) -> Preset:
    """
    默认的处理函数，根据规则处理预设数据并返回Preset对象。
    """
    # 合并 obligatory 和 optional 数据
    data = preset_data.get("obligatory", {})
    optional_data = preset_data.get("optional", {})
    data.update(optional_data)

    # 处理 title
    if not data.get("title"):
        data["title"] = data.get("name")

    # 处理 avatar
    if not data.get("avatar"):
        preset_name = data.get("name")
        if preset_name:
            # 查找当前目录下所有可能的图片文件
            possible_extensions = [".png", ".jpg", ".jpeg", ".gif", ".webp"]
            found_avatar_path = None
            for ext in possible_extensions:
                temp_path = f"{preset_name}{ext}"
                if os.path.exists(temp_path):
                    found_avatar_path = temp_path
                    break
            
            if found_avatar_path:
                with open(found_avatar_path, "rb") as image_file:
                    data["avatar"] = base64.b64encode(image_file.read()).decode("utf-8")

    # 处理 author
    if not data.get("author"):
        data["author"] = config.Author


    # 处理 instanceId
    if config.NekroInstanceID:
        data["instance_id"] = config.NekroInstanceID

    # 创建Preset实例
    try:
        return Preset(**data)
    except TypeError as e:
        raise ValueError(f"处理后的数据与Preset结构不匹配: {e}")


def read_preset(
    file_path: str,
    handle_function: Callable[[Any], Any] = default_handle_for_read_preset,
) -> Any:
    """
    从TOML文件中读取预设数据，转换为指定结构，并使用提供的函数进行处理。

    Args:
        file_path: TOML文件的路径。
        target_structure: 目标数据结构（例如dataclass），默认为Preset。
        handle_function: 用于处理转换后对象的函数。

    Returns:
        处理后的对象。
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"预设文件未找到: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = toml.load(f)

    # 传递整个toml数据给处理函数
    return handle_function(data)