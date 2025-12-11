# 项目重构进度

## 已完成

- [x] **代码结构重构**:
  - 已经将原有的 `@api` 和 `@schemas` 目录重构为 `@entity` 和 `@utils` 目录。
  - `@entity` 目录现在包含项目的数据结构定义（例如 `Preset` dataclass）。
  - `@utils` 目录包含项目的工具函数，例如与云端API交互的函数 (`cloud.py`) 和读取配置文件的函数 (`read_preset.py`)。

- [x] **配置中心化**:
  - 创建了 `@config/config.py` 模块，用于统一读取和管理 `.env` 文件中的环境变量。
  - `utils/read_preset.py` 现在使用 `@config/config.py` 来获取环境变量，移除了对 `utils/read_env.py` 的依赖。
  - 删除了冗余的 `utils/read_env.py` 文件。

- [x] **功能实现**:
  - 实现了 `utils/read_preset.py` 中的 `read_preset` 函数，该函数可以：
    - 读取 TOML 格式的预设文件。
    - 处理 `[obligatory]` 和 `[optional]` 部分。
    - 根据规则自动填充 `title`, `avatar`, `author`, 和 `instanceId` 等字段。
    - 支持自定义目标数据结构和处理函数。
  - 实现了 `utils/cloud.py` 中的云端API交互函数，使用 `httpx` 库进行异步HTTP请求。

## 下一步

- [ ] 根据新的代码结构，审查和更新项目其他部分（例如 `scripts` 目录下的脚本）的导入和调用方式。
- [ ] 编写或更新单元测试，确保重构后的代码能够正常工作。
- [ ] 完善文档，为新的模块和函数添加更详细的说明。
