# nekro_agent/tools/telemetry_util.py
# Decreased(Not Used AnyMore)
import hashlib
import json
import os
import platform
import socket
import uuid
from pathlib import Path
from typing import Dict, Optional
import logging

import sys

# 确保项目根目录在 sys.path 中（从 scripts 到仓库根）
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Avoid importing the top-level `nekro_agent` package here because its __init__ has
# side-effects (starts tasks, imports nonebot, etc.). Instead, compute CONFIG_DIR
# from the DATA_DIR environment variable (OsEnv.DATA_DIR default is './data').
DATA_DIR = os.getenv("DATA_DIR", "./data")
CONFIG_DIR = Path(DATA_DIR) / "configs"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Use a local logger instead of importing nekro_agent.core.logger
logger = logging.getLogger("nekro_agent.instance_id")
logger.addHandler(logging.NullHandler())


_INSTANCE_ID: Optional[str] = None
_CORE_VERSION: Optional[str] = "v2"

def get_system_info() -> Dict[str, str]:
    """获取系统信息（仅返回用于 fingerprint 的字段）

    Returns:
        Dict[str, str]: 系统信息字典
    """
    # Only collect hostname and platform because those are the only fields used in the fingerprint.
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
    }


def generate_instance_id() -> str:
    """生成实例唯一ID

    基于当前系统环境和硬件信息生成一个唯一ID

    Returns:
        str: 实例唯一ID
    """
    global _INSTANCE_ID
    if _INSTANCE_ID is not None:
        return _INSTANCE_ID

    instance_id_path = CONFIG_DIR / "instance.json"
    if instance_id_path.exists():
        try:
            instance_data = json.loads(instance_id_path.read_text())
            _core_version: str = instance_data.get("core_version", "")
            _instance_id: str = instance_data["instance_id"]
            _fingerprint: str = instance_data["fingerprint"]
            if _core_version != _CORE_VERSION:
                raise ValueError(f"核心版本不匹配: {_core_version} != {_CORE_VERSION}")  # noqa: TRY301
            if (
                isinstance(_instance_id, str)
                and isinstance(_fingerprint, str)
                and _instance_id == hashlib.sha256(_fingerprint.encode()).hexdigest()
            ):
                _INSTANCE_ID = _instance_id
                return _instance_id
        except Exception as e:
            logger.warning(f"读取实例ID失败: {e} 重新生成实例 ID...")

    # 收集环境信息
    system_info = get_system_info()

    # 获取cpu信息（延迟导入 psutil，兼容系统没有安装 psutil 的情况）
    try:
        import psutil as _psutil  # type: ignore
        cpu_count = _psutil.cpu_count() or os.cpu_count() or 0
        memory_info = str(_psutil.virtual_memory().total)
    except Exception:
        logger.warning("psutil 库不可用，使用降级方案获取硬件信息")
        cpu_count = os.cpu_count() or 0
        memory_info = "unknown"

    # 获取环境变量指纹
    env_keys = sorted(os.environ.keys())
    env_fingerprint = ",".join(env_keys)

    # 获取计算机UUID（如有）
    computer_id = ""
    try:
        if platform.system() == "Windows":
            computer_id = os.popen("wmic csproduct get uuid").read()
        elif platform.system() == "Linux":
            with Path("/var/lib/dbus/machine-id").open() as f:
                computer_id = f.read()
        elif platform.system() == "Darwin":  # macOS
            computer_id = os.popen('ioreg -rd1 -c IOPlatformExpertDevice | grep -i "UUID" | cut -c27-62').read()
        # strip whitespace/newlines for more stable fingerprint
        computer_id = (computer_id or "").strip()
        if not computer_id:
            # fallback to MAC-based identifier if platform-specific ID not found
            computer_id = str(uuid.getnode())
    except Exception:
        computer_id = str(uuid.getnode())  # 使用网卡MAC地址的整数表示作为备选

    # 组合所有信息
    fingerprint = (
        f"{system_info['hostname']}|"
        f"{system_info['platform']}|"
        f"{computer_id}|"
        f"{cpu_count}|"
        f"{memory_info}|"
        f"{env_fingerprint}|"
        f"{_CORE_VERSION}"
    )

    # 生成 SHA256 哈希
    _INSTANCE_ID = hashlib.sha256(fingerprint.encode()).hexdigest()
    instance_id_path.parent.mkdir(parents=True, exist_ok=True)
    instance_id_path.write_text(
        json.dumps(
            {
                "instance_id": _INSTANCE_ID,
                "fingerprint": fingerprint,
                "core_version": _CORE_VERSION,
            },
        ),
    )
    return _INSTANCE_ID

if __name__=="__main__":
    print("Instance ID:", generate_instance_id())
