# Nekro Agent - Preset (人设) API 文档

本文档记录与人设（Preset）相关的所有 API，包含本地管理接口、云端市场相关接口以及与 Nekro Cloud 的交互说明。文档使用中文，本地接口优先列出；如有重复行为，以本地实现为准并标注与云端字段的映射。

注意：项目代码中本地路由前缀为 `/presets`（注意复数），云端市场路由前缀为 `/cloud/presets-market`，外部 Nekro Cloud 的 API（远端）示例前缀通常为 `/api/preset`。

## 认证

所有需要鉴权的接口都要求在 HTTP 头中携带认证：

- Header: `Authorization: Bearer <YOUR_API_KEY>`

（具体鉴权细节请参见项目的用户/权限服务）

---

## 本地人设管理 API（优先）

基础前缀: `/presets`

说明：以下接口由 `nekro_agent/routers/presets.py` 实现，访问受角色校验，默认需要管理员权限（Role.Admin）。

公共响应格式示例（项目使用 `Ret` 封装）：
{
  "code": 200,
  "msg": "操作结果描述",
  "data": ...
}

### 1. 获取人设标签统计
- 方法: GET
- 路径: `/presets/tags`
- 权限: 管理员
- 查询参数: 无
- 返回: 列表，每项为 `{ "tag": "标签名", "count": 数量 }`
- 备注: 按使用量降序（数量相同按字母升序）

### 2. 获取人设列表
- 方法: GET
- 路径: `/presets/list`
- 权限: 管理员
- 查询参数:
  - `page` (int, default=1)
  - `page_size` (int, default=20)
  - `search` (str, 可选): 模糊匹配 name/title/description
  - `tag` (str, 可选): 单标签（兼容旧参数）
  - `tags` (str, 可选): 多标签，逗号分隔，AND 逻辑
  - `remote_only` (bool, 可选): true 仅远程/云端人设，false 仅本地人设
- 返回 data 示例:
  {
    "total": 100,
    "items": [
      {
        "id": 1,
        "remote_id": "cloud-123",
        "on_shared": true,
        "name": "示例",
        "title": "标题",
        "avatar": "data:image/png;base64,...",
        "description": "描述",
        "tags": "tag1,tag2",
        "author": "作者",
        "is_remote": true,
        "create_time": "2023-01-01 12:00:00",
        "update_time": "2023-01-02 12:00:00"
      }
    ]
  }

### 3. 获取人设详情
- 方法: GET
- 路径: `/presets/{preset_id}`
- 权限: 管理员
- 路径参数: `preset_id` (int)
- 返回: 与列表项相同结构，但包含 `content`（人设完整内容）

### 4. 创建人设
- 方法: POST
- 路径: `/presets`  （注意：本地使用 `/presets`）
- 权限: 管理员
- 请求体 (JSON):
  - name: str (必填)
  - title: str (可选，若为空则使用 name)
  - avatar: str (必填) — Data URL / Base64 字符串（由 `/presets/upload-avatar` 推荐生成）
  - content: str (必填)
  - description: str (可选)
  - tags: str (可选) — 逗号分隔
  - author: str (可选，默认当前用户)
- 成功响应:
  { "code": 200, "msg": "创建成功", "data": { "id": 新建ID } }

### 5. 更新人设
- 方法: PUT
- 路径: `/presets/{preset_id}`
- 权限: 管理员
- 请求体 (JSON): 与创建相同字段，必填项仍需提供（路由实现使用 Body(...) 强制），额外字段：
  - remove_remote: bool (可选，默认 false) — 若为 true 且此预设有 remote_id 且未 on_shared，则会清除 remote_id
- 成功响应: { "code":200, "msg":"更新成功" }
- 错误情形: 人设不存在则返回失败信息

### 6. 删除人设
- 方法: DELETE
- 路径: `/presets/{preset_id}`
- 权限: 管理员
- 成功响应: { "code":200, "msg":"删除成功" }

### 7. 上传头像
- 方法: POST
- 路径: `/presets/upload-avatar`
- 权限: 管理员
- 请求格式: multipart/form-data
  - 字段: file (图片文件)
- 返回: { "code":200, "msg":"上传成功", "data": { "avatar": "data:image/...;base64,..." } }
- 备注: 服务端会读取文件并转换为 Base64 Data URL，调用 `process_image_data_url` 处理（压缩/裁剪等），具体限制（尺寸/大小）未在路由中硬编码，取决于工具函数实现。

### 8. 共享/撤回/同步（与云端交互的本地操作）
下列接口会与 Nekro Cloud 交互或影响本地 `remote_id`/`on_shared` 字段：

- 共享到云端
  - 方法: POST
  - 路径: `/presets/{preset_id}/share`
  - 权限: 管理员
  - 查询参数/Body: `is_sfw` (bool, default true) — 路由中为函数参数（FastAPI 会从 query/body 中解析）。
  - 逻辑与校验:
    - 必须存在 name/content/avatar/description
    - 若已有 `on_shared` 且 `remote_id` 则拒绝
    - 会构建 `PresetCreate` 并调用云端 `create_preset`
    - 成功后更新本地 `remote_id` 与 `on_shared`
  - 成功响应: { "code":200, "msg":"共享成功", "data": { "remote_id": "云端ID" } }

- 撤回共享（删除云端资源）
  - 方法: POST
  - 路径: `/presets/{preset_id}/unshare`
  - 权限: 管理员
  - 逻辑:
    - 仅当 `on_shared` 且有 `remote_id` 时可执行
    - 调用云端删除接口（会传 instance_id），无论成功与否都会把本地 `on_shared` 设为 false；仅当云端返回成功时才清空 `remote_id` 字段
  - 成功响应: { "code":200, "msg":"撤回共享成功" }

- 将本地修改同步到云端（覆盖云端）
  - 方法: POST
  - 路径: `/presets/{preset_id}/sync-to-cloud`
  - 权限: 管理员
  - 参数: `is_sfw` (bool, default true)
  - 逻辑: 仅在 `on_shared` 且 `remote_id` 存在时执行，构建 `PresetUpdate` 调用云端更新接口
  - 成功响应: { "code":200, "msg":"同步成功" }

- 从云端拉取最新并覆盖本地（云端优先）
  - 方法: POST
  - 路径: `/presets/{preset_id}/sync`
  - 权限: 管理员
  - 逻辑: 仅在 `remote_id` 存在时调用云端获取详情并覆盖本地对应字段（name/title/avatar/content/description/tags/author）
  - 成功响应: { "code":200, "msg":"同步成功" }

### 9. 刷新共享状态
- 方法: POST
- 路径: `/presets/refresh-shared-status`
- 权限: 管理员
- 逻辑: 调用云端 `list_user_presets`，比对本地 `remote_id` 列表，更新本地 `on_shared` 字段
- 返回包含更新统计: { "code":200, "msg":"刷新成功", "data": { "updated_count": n, "total_cloud_presets": m } }

---

## 云端市场（Cloud Presets Market）API（代理本地与远端数据交互）

基础前缀: `/cloud/presets-market`

说明：以下接口由 `nekro_agent/routers/cloud/presets_market.py` 实现，主要用于展示云端市场数据并在本地下载云端人设。

### 1. 获取云端人设列表
- 方法: GET
- 路径: `/cloud/presets-market/list`
- 权限: 管理员
- 查询参数:
  - `page` (int, ge=1, default=1)
  - `page_size` (int, ge=1, le=100, default=12)
  - `keyword` (str, 可选)
  - `tag` (str, 可选)
- 逻辑:
  - 调用云端 `list_presets`，并把云端项与本地 `remote_id` 做比对，返回 `is_local` 标识
- 返回 data 示例:
  {
    "total": 200,
    "items": [ { "remote_id":"...", "is_local": false, "name":"...", "title":"...", "avatar":"...", "content":"...", "description":"...", "tags":"...", "author":"...", "create_time":"...", "update_time":"..." } ],
    "page": 1,
    "page_size": 12,
    "total_pages": 17
  }

### 2. 下载云端人设到本地
- 方法: POST
- 路径: `/cloud/presets-market/download/{remote_id}`
- 权限: 管理员
- 路径参数: `remote_id` (str)
- 逻辑:
  - 若本地已存在同 remote_id 则拒绝
  - 调用云端获取详情，转换并写入本地 DBPreset（保留 `remote_id`，`on_shared` = 云端返回的 `is_owner`）
- 成功响应: { "code":200, "msg":"下载成功" }

---

## 与 Nekro Cloud 的交互（远端 API 映射与字段说明）

本项目通过 `nekro_agent/systems/cloud/api/preset.py` 调用远端 API。下面列出远端模型与本地字段的映射与注意点。

远端请求模型: `PresetCreate` / `PresetUpdate`（见 `nekro_agent/systems/cloud/schemas/preset.py`）
- 字段（发送到云端）:
  - name (str)
  - title (str)
  - avatar (str) — Base64 Data URL
  - content (str)
  - description (str)
  - tags (str) — 逗号分隔
  - author (str)
  - extData (str) — 对应本地 `ext_data`
  - isSfw (bool) — 是否为安全内容
  - instanceId (str) — 本次操作的实例 ID（客户端/服务端生成）

远端重要响应模型（节选）:
- PresetCreateResponse.data.id: 创建后返回的 `id`（字符串）
- PresetDetail: 远端详情包含 `id`, `name`, `title`, `avatar`, `content`, `description`, `tags`, `author`, `isOwner`（是否为当前用户拥有）, `extData`, `createdAt`, `updatedAt`
- PresetListResponse: 包含 `items` 列表与 `total/page/pageSize/totalPages`

映射与差异说明：
- 本地 `DBPreset.remote_id` 对应远端 `id`（字符串）
- 本地 `on_shared` 通常与远端的 `isOwner`/是否存在于用户云端列表联合决定，本地会在某些操作后更新该字段
- 本地 `ext_data` 对应远端 `extData`（注意空串/空对象的处理）
- 时间字段：本地使用 `create_time/update_time`（datetime 字符串），远端返回 `createdAt/updatedAt`（字符串）

---

## 本地数据库模型字段参考 (`nekro_agent/models/db_preset.py`)
- id: int (本地主键)
- remote_id: str | null — 远端预设 ID
- on_shared: bool — 是否标记为已共享
- name: str — 人设名
- title: str — 标题
- avatar: text — Base64 Data URL（图片）
- content: text — 人设主要内容（会被注入到系统/assistant prompt）
- description: text — 详细描述
- tags: str — 逗号分隔字符串
- ext_data: json | null — 扩展字段
- author: str
- create_time / update_time: datetime

---

## 注意事项与边界情况
- 路由权限：多数接口被 `@require_role(Role.Admin)` 包裹，确保调用者角色正确。
- avatar 的格式：路由中以 Data URL/base64 形式传输；建议客户端先调用 `/presets/upload-avatar` 上传图片获取处理后的 Data URL 再用于创建/更新。
- 标签过滤：本地 `list` 支持 `tag` 与 `tags`（兼容旧参数）；`tags` 支持逗号分隔的 AND 逻辑过滤。
- 远端交互失败处理：部分本地接口在云端失败时仍会调整本地字段（例如 `unshare` 会在失败/成功均把 `on_shared` 设为 false，但仅在云端成功时清空 `remote_id`）。
- 字段长度/校验：远端 schema 对某些字段有长度限制（如 name/title/content/description 等），本地在构建 `PresetCreate`/`PresetUpdate` 时会依赖远端的 pydantic 校验（可能抛出异常）。

---

## 示例（简短）

1) 上传头像并创建人设（伪请求流程）:
- POST `/presets/upload-avatar` multipart/form-data file -> 得到 `avatar` Data URL
- POST `/presets` JSON body 包含 `avatar` 与其它字段 -> 返回 `id`

2) 共享到云端:
- POST `/presets/{preset_id}/share?is_sfw=true` -> 成功返回 `remote_id`

3) 在云端市场下载到本地:
- POST `/cloud/presets-market/download/{remote_id}` -> 成功则在本地生成一条 DBPreset 记录
