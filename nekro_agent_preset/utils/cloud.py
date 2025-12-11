from typing import Dict, Optional, Union
import httpx
from nekro_agent_preset.entity.preset import (
    Preset,
    BasicResponse,
    PresetCreateResponse,
    PresetDetailResponse,
    UserPresetListResponse,
)
from logging import getLogger
from nekro_agent_preset.config import config

logger = getLogger(__name__)

baseURL = config.NEKRO_API_URL


async def create_preset(preset_data: Preset, api_key: str) -> PresetCreateResponse:
    """创建人设资源

    Args:
        preset_data: 人设数据
        api_key: API Key

    Returns:
        PresetCreateResponse: 创建响应结果
    """
    try:
        async with httpx.AsyncClient(
            base_url=baseURL,
            headers={"X-API-Key": f"{api_key}", "Content-Type": "application/json"},
        ) as client:
            response = await client.post(
                url="/api/preset",
                json={
                    "name": preset_data.name,
                    "title": preset_data.title,
                    "avatar": preset_data.avatar,
                    "content": preset_data.content,
                    "description": preset_data.description,
                    "tags": preset_data.tags,
                    "author": preset_data.author,
                    "extData": preset_data.ext_data,
                    "isSfw": preset_data.is_sfw,
                    "instanceId": preset_data.instance_id,
                },
            )
            response.raise_for_status()
            return PresetCreateResponse(**response.json())
    except Exception as e:
        logger.error(f"创建人设资源发生错误: {e}")
        return PresetCreateResponse.process_exception(e)


async def update_preset(
    preset_id: str, preset_data: Preset, api_key: str
) -> BasicResponse:
    """更新人设资源

    Args:
        preset_id: 人设ID
        preset_data: 更新的人设数据
        api_key: API Key

    Returns:
        BasicResponse: 响应结果
    """
    try:
        async with httpx.AsyncClient(
            base_url=baseURL,
            headers={"X-API-Key": f"{api_key}", "Content-Type": "application/json"},
        ) as client:
            response = await client.put(
                url=f"/api/preset/{preset_id}",
                json={
                    "name": preset_data.name,
                    "title": preset_data.title,
                    "avatar": preset_data.avatar,
                    "content": preset_data.content,
                    "description": preset_data.description,
                    "tags": preset_data.tags,
                    "author": preset_data.author,
                    "extData": preset_data.ext_data,
                    "isSfw": preset_data.is_sfw,
                    "instanceId": preset_data.instance_id,
                },
            )
            response.raise_for_status()
            return BasicResponse(**response.json())
    except Exception as e:
        logger.error(f"更新人设资源发生错误: {e}")
        return BasicResponse.process_exception(e)

async def delete_preset(
    preset_id: str, instance_id: str, api_key: str
) -> BasicResponse:
    """删除人设资源
    Args:
     preset_id: 人设ID
     instance_id: 实例ID
    api_key: API Key

    Returns:
        BasicResponse: 响应结果
    """
    try:
        async with httpx.AsyncClient(
            base_url=baseURL,
            headers={"X-API-Key": f"{api_key}", "Content-Type": "application/json"},
        ) as client:
            response = await client.delete(
                url=f"/api/preset/{preset_id}",
                params={"instanceId": instance_id},
            )
            response.raise_for_status()
            return BasicResponse(**response.json())
    except Exception as e:
        logger.error(f"删除人设资源发生错误: {e}")
        return BasicResponse.process_exception(e)

async def list_user_presets(api_key: str) -> UserPresetListResponse:
    """获取用户上传的人设列表
    Returns:
        UserPresetListResponse: 简化版人设列表响应
    """
    try:
        async with httpx.AsyncClient(
            base_url=baseURL,
            headers={"X-API-Key": f"{api_key}", "Content-Type": "application/json"},
        ) as client:
            response = await client.get(url="/api/preset/user")
            response.raise_for_status()
            return UserPresetListResponse(**response.json())
    except Exception as e:
        logger.error(f"获取用户上传人设列表发生错误: {e}")
        return UserPresetListResponse.process_exception(e)

async def get_preset(preset_id: str) -> PresetDetailResponse:
    """获取人设详情
    Args:
        preset_id: 人设ID
    Returns:
        PresetDetailResponse: 人设详情响应
    """
    try:
        async with httpx.AsyncClient(base_url=baseURL) as client:
            response = await client.get(url=f"/api/preset/{preset_id}")
            response.raise_for_status()
            return PresetDetailResponse.model_validate(response.json())
    except Exception as e:
        logger.error(f"获取人设详情发生错误: {e}")
        return PresetDetailResponse.process_exception(e)
