# Nekro Cloud — 本地与云端交互说明（Preset / 云端市场）

本文档详细说明本地服务如何与 Nekro Cloud（云端市场）交互，重点以 `/cloud/presets-market/list` 的执行流程为例，逐步追踪到实际发出的 HTTP 请求、目标服务器、请求头/参数、返回体的本地处理逻辑，以及与其他云端预设相关的交互（下载、共享、同步、删除）。

重要文件参考（实现位置）
- 本地路由（云端市场代理）：`nekro_agent/routers/cloud/presets_market.py`
- 云端 API 客户端封装：`nekro_agent/systems/cloud/api/preset.py`
- HTTP 客户端创建：`nekro_agent/systems/cloud/api/client.py`
- 云端 schema 与响应结构：`nekro_agent/systems/cloud/schemas/preset.py`
- 本地人设模型：`nekro_agent/models/db_preset.py`
- 本地人设路由（共享/同步等）：`nekro_agent/routers/presets.py`

概述：
- 本地向云端发起 HTTP 请求由 `get_client()` 创建的 `httpx.AsyncClient` 负责，`base_url` 来源于环境变量 `NEKRO_CLOUD_API_BASE_URL`（默认：`https://community.nekro.ai`），请求默认会包含 `X-API-Key`（来自 `config.NEKRO_CLOUD_API_KEY`）与 `Content-Type: application/json`。
- 不同的云端 API 调用会选择是否必须鉴权（`get_client(require_auth=True)` 会校验 `config.ENABLE_NEKRO_CLOUD` 与 `config.NEKRO_CLOUD_API_KEY`，若不满足会抛出异常）。

---

一、/cloud/presets-market/list 调用链（流程详述）

请求入口：
- 本地路由：`GET /cloud/presets-market/list`（实现于 `nekro_agent/routers/cloud/presets_market.py`）
- 路径示例： `/cloud/presets-market/list?page=1&page_size=12&keyword=xxx&tag=角色`。

路由内部逻辑（概要）：
1. 路由函数收集 query 参数（`page`, `page_size`, `keyword`, `tag`）并调用库函数 `list_presets`（定义于 `nekro_agent/systems/cloud/api/preset.py`）。
2. `list_presets` 构建请求参数字典：
   - `page` -> `page`（整型）
   - `page_size` -> `pageSize`（整型）
   - 可选 `keyword` -> `keyword`
   - 可选 `tag` -> `tag`
   - 如果 `config.ENSURE_SFW_CONTENT` 为 False，会额外加入 `allowNsfw=true`（允许返回 NSFW 内容）。
3. `list_presets` 调用 `get_client()`（注意：此处 `require_auth=False`，即不会强制校验 API Key，但仍使用 `OsEnv.NEKRO_CLOUD_API_BASE_URL` 作为 `base_url`，且请求头会包含 `X-API-Key` 与 `Content-Type`，其中 `X-API-Key` 可能为空）。
4. 使用 `httpx.AsyncClient` 发起 GET 请求：
   - 完整请求 URL = `${NEKRO_CLOUD_API_BASE_URL}/api/preset`，例如 `https://community.nekro.ai/api/preset`
   - 请求方法：GET
   - 查询参数：`page`, `pageSize`, `keyword?`, `tag?`, `allowNsfw?`
   - Header 示例：
     - `X-API-Key: <config.NEKRO_CLOUD_API_KEY>`（可能为空，除非已配置）
     - `Content-Type: application/json`
5. 云端返回后，`list_presets` 使用 `PresetListResponse(**response.json())` 将 JSON 反序列化为 Pydantic 模型（`nekro_agent/systems/cloud/schemas/preset.py` 中定义）。
6. `nekro_agent/routers/cloud/presets_market.py` 中的路由接收到 `PresetListResponse` 后：
   - 检查 `response.success`（`BasicResponse` 的 `success` 字段），若为 False 则返回失败给客户端。
   - 若 `response.data` 或 `response.data.items` 为空，则返回空列表给前端。
   - 否则，收集云端返回的所有 `remote_id`（即 `item.id` 列表），并查询本地数据库（`DBPreset`）以判断哪些云端项已存在于本地（通过 `DBPreset.filter(remote_id__in=remote_ids).values("remote_id")`）。
   - 对每个云端项，构建本地返回对象，将远端字段（`id/name/title/avatar/content/description/tags/author/createdAt/updatedAt`）映射到本地展示字段，并额外添加 `is_local`（布尔，表示本地数据库中是否存在该 `remote_id`）。
   - 将聚合结果按本地接口的响应格式返回给调用者（例如 Web UI）。

示例：云端请求（由本地发出）
GET https://community.nekro.ai/api/preset?page=1&pageSize=12&keyword=猫&tag=萌
Headers:
  X-API-Key: nk-xxxxx
  Content-Type: application/json

服务器（云端）返回（示例）:
{
  "success": true,
  "message": "",
  "data": {
    "items": [
      {
        "id": "abc123",
        "name": "小猫",
        "title": "萌喵人设",
        "avatar": "data:image/png;base64,...",
        "content": "你是...",
        "description": "详细描述",
        "tags": "萌,猫",
        "author": "作者A",
        "isOwner": false,
        "extData": "{}",
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-02-01T00:00:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "pageSize": 12,
    "totalPages": 9
  }
}

本地路由返回给前端（示例）:
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "total": 100,
    "items": [
      {
        "remote_id": "abc123",
        "is_local": false,
        "name": "小猫",
        "title": "萌喵人设",
        "avatar": "data:image/png;base64,...",
        "content": "你是...",
        "description": "详细描述",
        "tags": "萌,猫",
        "author": "作者A",
        "create_time": "2025-01-01T00:00:00Z",
        "update_time": "2025-02-01T00:00:00Z"
      }
    ],
    "page": 1,
    "page_size": 12,
    "total_pages": 9
  }
}

---

二、其他相关云端交互（下载/共享/更新/删除）

下表列出项目中与云端交互的主要调用、鉴权要求以及本地如何处理响应：

1) 获取云端详情（用于下载/同步）
- 调用方：`nekro_agent/routers/cloud/presets_market.py` 的 `download_preset`，以及本地 `presets` 路由的 `sync`。
- 使用函数：`get_preset(preset_id: str)`（`nekro_agent/systems/cloud/api/preset.py`）
- HTTP 调用：GET `${NEKRO_CLOUD_API_BASE_URL}/api/preset/{preset_id}`（`get_client()` 未启用 require_auth。）
- 本地处理：返回 `PresetDetailResponse` -> 路由会读取 `response.data` 并将字段写入本地 `DBPreset`（包括 `remote_id`, `on_shared` = `isOwner` 等）。

2) 下载到本地（路由行为）
- 路由：`POST /cloud/presets-market/download/{remote_id}`
- 行为：先检查本地是否已存在 `remote_id`，若存在则拒绝；否则调用 `get_preset` 获取远端详情并创建本地 `DBPreset` 记录。

3) 在云端创建/共享（本地 -> 云端）
- 触发点：`POST /presets/{preset_id}/share`（本地路由）
- 使用函数：`create_preset(preset_data: PresetCreate)`，这是云端 API 的 POST `/api/preset`。
- 鉴权：`get_client(require_auth=True)`，需要 `config.ENABLE_NEKRO_CLOUD` 为 True 且 `config.NEKRO_CLOUD_API_KEY` 非空，否则抛出 `NekroCloudDisabled` 或 `NekroCloudAPIKeyInvalid`。
- 请求体：字段映射见 `PresetCreate`（`name/title/avatar/content/description/tags/author/extData/isSfw/instanceId`）。`instanceId` 由本地函数 `generate_instance_id()` 生成以标识此次请求实例。
- 本地处理：云端返回创建成功后（`data.id`），路由将 `preset.remote_id = response.data.id`，并设置 `on_shared = True`，保存到本地 DB。

4) 在云端更新（本地->云端）
- 触发点：`POST /presets/{preset_id}/sync-to-cloud` 或 `PUT /api/preset/{id}`（云端）
- 使用函数：`update_preset(preset_id, preset_data)`（require_auth=True）
- 本地处理：调用成功返回后仅返回成功消息（云端的具体变更由云端管理）。

5) 在云端删除 / 撤回共享（本地发起）
- 触发点：`POST /presets/{preset_id}/unshare`
- 使用函数：`delete_preset(preset_id, instance_id)`（require_auth=True）
- 本地处理：无论云端删除是否成功，本地会将 `on_shared = False`；仅当云端返回 success 时才清空 `remote_id` 字段。

---

三、鉴权与错误处理细节

- `get_client(require_auth=True)` 的行为：
  - 若 `OsEnv.NEKRO_CLOUD_API_BASE_URL` 未配置或 `config.ENABLE_NEKRO_CLOUD` 为 False，会抛出 `NekroCloudDisabled`。
  - 若 `config.NEKRO_CLOUD_API_KEY` 为空或未配置，会抛出 `NekroCloudAPIKeyInvalid`。
  - 成功时返回的 `httpx.AsyncClient` 会以 `base_url=NEKRO_CLOUD_API_BASE_URL` 和 headers 包含 `X-API-Key` 与 `Content-Type: application/json`。

- `BasicResponse.process_exception`（`nekro_agent/systems/cloud/schemas/base.py`）
  - 对异常 `NekroCloudDisabled` 返回友好提示（告诉用户云服务未启用）。
  - 对 HTTP 401/403 返回友好提示（API Key 无效）。
  - 其他异常会向上抛出或记录日志。

- 注意：`list_presets` 与 `get_preset` 使用 `get_client()`（不强制鉴权），因此在未配置 API Key 或禁用 Nekro Cloud 时仍可能会对 `NEKRO_CLOUD_API_BASE_URL` 发起请求（如果该 URL 可公开访问，可能会返回数据），但某些写操作（create/update/delete/list_user_presets）强制 require_auth=True，若未启用云或未配置 Key，将直接失败并触发 `NekroCloudDisabled` 或 `NekroCloudAPIKeyInvalid`。

---

四、推荐的客户端/运维检查点

- 若希望使用共享/上传/删除等写操作，务必在配置中设置：
  - `config.ENABLE_NEKRO_CLOUD = True`
  - `config.NEKRO_CLOUD_API_KEY = "nk-xxxx..."` 或环境变量 `NEKRO_CLOUD_API_KEY`
  - `OsEnv.NEKRO_CLOUD_API_BASE_URL` 指向你希望调用的云端地址（默认 `https://community.nekro.ai`）。

- 若仅需要浏览云端市场（list/get），可以不配置 API Key，但依据云端策略某些资源可能需要认证才能返回完整数据或标记 `isOwner`。

- 日志与排查：
  - 本地会记录云端请求错误（`logger.error` / `logger.exception`），出现 401/403 时 `BasicResponse.process_exception` 会把错误转换为可读消息供上层路由返回。

---

五、快速示意（序列）

1. 浏览列表
User -> GET /cloud/presets-market/list -> local router -> list_presets() -> GET https://community.nekro.ai/api/preset?params -> cloud 返回 -> local 比对 DBPreset -> 返回给 User。

2. 下载云端人设
User -> POST /cloud/presets-market/download/{remote_id} -> local router -> get_preset(remote_id) -> GET https://community.nekro.ai/api/preset/{remote_id} -> cloud 返回 -> local 写入 DBPreset -> 返回给 User。

3. 共享到云端
User -> POST /presets/{preset_id}/share -> local router 构建 PresetCreate -> create_preset() -> POST https://community.nekro.ai/api/preset (X-API-Key required) -> cloud 返回 id -> 本地更新 remote_id/on_shared -> 返回给 User。
