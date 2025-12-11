from dataclasses import dataclass
from typing import List, Optional

from httpx import HTTPStatusError
from pydantic import BaseModel, Field


@dataclass
class Preset:
    name: str
    title: str
    avatar: str
    content: str
    description: str
    tags: str
    author: str
    ext_data: str
    is_sfw: bool
    instance_id: str


@dataclass
class PresetDetail:
    id: str
    name: str
    title: str
    avatar: str
    content: str
    description: str
    tags: str
    author: str
    is_owner: bool = False
    ext_data: Optional[str] = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# 大概只会用上面两个


@dataclass
class PresetListItem(PresetDetail):
    pass


@dataclass
class PresetListData:
    items: List[PresetListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


@dataclass
class UserPresetItem:
    id: str
    name: str
    title: str


@dataclass
class UserPresetListData:
    items: List[UserPresetItem]
    total: int


@dataclass
class PresetCreateResponseData:
    id: str


class NekroCloudDisabled(Exception):
    pass


class NekroCloudAPIKeyInvalid(Exception):
    pass


class BasicResponse(BaseModel):
    """基本响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="消息")
    error: Optional[str] = Field(default=None, description="错误信息")

    @classmethod
    def process_exception(cls, e: Exception):
        if isinstance(e, NekroCloudDisabled):
            return cls(
                success=False,
                message="Nekro AI 社区服务遥测未启用，当前实例暂无权限使用",
                error="Nekro AI 社区服务遥测未启用，当前实例暂无权限使用",
            )
        if isinstance(e, HTTPStatusError) and e.response.status_code in [401, 403]:
            return cls(
                success=False,
                message="Nekro AI 社区 API Key 无效，请前往 Nekro AI 社区获取并配置",
                error=e.response.text,
            )
        raise e

    class Config:
        extra = "ignore"




class PresetCreateResponse(BasicResponse):
    """创建人设响应模型"""

    data: Optional[PresetCreateResponseData] = Field(None, description="响应数据")



class UserPresetListResponse(BasicResponse):
    """用户人设列表响应模型"""

    data: Optional[UserPresetListData] = Field(None, description="响应数据")


class PresetDetailResponse(BasicResponse):
    """人设详情响应模型"""

    data: Optional[PresetDetail] = Field(None, description="响应数据")