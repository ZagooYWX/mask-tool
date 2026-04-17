# mask-tool

本地文件脱敏工具（CLI），用于在将文件提交给AI或外部系统前进行敏感信息脱敏，并支持后续还原（可逆脱敏）。

## 特性

- **可逆脱敏**：敏感信息替换为唯一Token（如 `[COMPANY_001]`），支持反脱敏还原
- **不可逆脱敏**：替换为 `***` 或随机字符串
- **多格式支持**：Word(.docx)、Excel(.xlsx)、PowerPoint(.pptx)、PDF
- **智能识别**：正则规则 + 词典匹配，按置信度分级处理
- **三种运行模式**：strict / smart / aggressive
- **本地运行**：所有处理本地执行，禁止调用外部API

## 快速开始

```bash
# 安装
pip install -e .

# 脱敏处理
mask-tool mask input.docx --mode smart --output ./output/

# 查看检测结果（不执行脱敏）
mask-tool inspect input.docx

# 反脱敏（还原原文）
mask-tool unmask masked.docx --mapping mapping.json --output ./restored/
```

## 项目结构

```
mask-tool/
├── src/mask_tool/
│   ├── cli/              # CLI入口
│   ├── models/           # 核心数据模型
│   ├── core/             # 核心业务（检测/脱敏/流水线）
│   ├── adapters/         # 文件格式适配器
│   ├── store/            # 持久化（映射表/词库）
│   └── utils/            # 工具函数
├── config/               # 配置文件
├── tests/                # 测试
└── samples/              # 示例文件
```

## 运行模式

| 模式 | 说明 |
|------|------|
| `strict` | 仅处理用户词库，适合高安全场景 |
| `smart`（默认） | 词库 + 正则 + NER，适合大多数场景 |
| `aggressive` | 高召回优先，适合AI前处理 |

## 脱敏对象

支持以下类别的敏感信息：
- 公司名称（我方/对方/关联方）
- 政府机构
- 人名
- 地名
- 项目名称
- 标的物名称
- 金额（支持模糊化，如 1.2亿 → 1亿+）
- 自定义关键词

## 配置

编辑 `config/default.yaml` 自定义配置，或通过命令行参数覆盖。

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest
```

## License

MIT
