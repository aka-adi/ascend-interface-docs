---
name: ascend-interface-docs
description: Use when writing/reviewing Ascend TLA/TileLang interface specs, 接口注释, 接口规格文档, @builtin docstrings, Sphinx autosummary RST pages, or verifying dtype/mask/mode/位宽 contracts against AVE TD and CCE overloads.
---

# Ascend Interface Documentation

面向 Ascend TLA / TileLang 接口规格整理、`@builtin` docstring、TA 自动文档入口和规格复核。

## 可移植性约定

本 skill 面向外部复用，不依赖个人目录或固定安装路径。所有命令使用环境变量：

```bash
REPO_ROOT=/path/to/repo
DOCS_DIR="$REPO_ROOT/docs/zh"
PYTHON=/path/to/python
SPHINX_MODULE=sphinx
SKILL_DIR=/path/to/skills/ascend-interface-docs
CANN_ROOT=/path/to/cann
PREVIEW_DIR="${TMPDIR:-/tmp}/ascend-interface-docs-preview"
PORT=8766
```

没有设置时，使用当前仓库、`python3`、`$TMPDIR` 等通用默认值。

## 核心原则

1. **先确认实现，再写文档**
   - 找实际 Python 定义、签名、默认值、返回值和 lowering 路径。
   - 不根据接口名猜 dtype、mask、mode、位宽或语义。

2. **AVE TD、lowering、CCE stub 多层交叉验证**
   - AVE TD：`$REPO_ROOT/third_party/ascend/AscendNPU-IR/bishengir/include/bishengir/Dialect/HIVMAVE/IR/HIVMAVEOps.td`
   - AVE intrinsic：`lib/Conversion/HIVMAVEToAVEIntrin/HIVMAVEToAVEIntrin.cpp`
   - AVE library-call：`lib/Conversion/HIVMAVEToStandard/HIVMAVEToStandard.cpp`
   - CCE overload：`$CANN_ROOT/tools/cpudebug/include/stub_fun.h`
   - Python 前端通常不做完整 dtype 校验，不能只看 Python。

3. **区分 TLA、TileLang、AVE**
   - TLA：`triton.language.extra.tla`，常见 `@builtin`。
   - TileLang：`tilelang.ascend.language`，常见普通函数 + `tirx.call_intrin`。
   - AVE：HIVMAVE dialect。
   - `T.simd.*` / `T.ascend_*` 是 TileLang 命名，不要误写成 TLA。

4. **保守文档**
   - 只承诺已确认、可验证、无隐式降级的行为。
   - 未确认能力放入“不确定点”，不写成正式契约。
   - 业务/模型特定边界只在用户明确要求时写入文档。

5. **评审门禁**
   - 用户要求“先整理规格、确认后再写代码”时：
     - 只生成评审文档；
     - 列出不确定点；
     - 不改源码；
     - 等用户确认后再写 docstring。

## 规格优先级矩阵

规格判断分成“语义”和“可用性”两层，不能混成单一线程。

### 语义优先级

用于判断“接口到底是什么意思”：

```text
用户确认的规格
  > AVE TD 定义/描述
  > AVE lowering 实现
  > CCE intrinsic 实现
  > 测试/示例
```

### dtype/可用性优先级

用于判断“这个 dtype 能否使用”：

```text
用户确认的规格
  > Python 前端实际可调用范围
  > AVE intrinsic registry
  > AVE library-call fallback
  > CCE stub overload
  > 测试覆盖
```

正式契约取保守交集：

```text
Python 前端可接受
∩ AVE intrinsic / library-call 实际路径
∩ CCE stub 实际 overload
```

如果三者不一致：

```text
结论：不确定
```

不要因为“Python 前端没拒绝”就写成支持，  
也不要因为“AVE TD 允许”就写成可编译。

| 层级 | 作用 | 能否单独作为正式契约 |
|---|---|---|
| 用户确认规格 | 最终产品决策 | 可以 |
| Python 前端 | API 签名、默认值、前端校验 | 只能说明“可调用” |
| AVE TD | op 语义、ODS 类型可能性 | 只能说明“语义/形式允许” |
| AVE intrinsic registry | 单寄存器实际 lowering | 重要可用性依据 |
| AVE library-call fallback | i64 等特殊路径 | 重要可用性依据 |
| CCE stub / codegen | 最终编译可用性 | 重要可用性依据 |
| 测试/示例 | 已验证行为 | 只能作为证据 |

## 工作流

### 1. 确认接口是否存在

```bash
rg -n '^def <name>\b' "$REPO_ROOT" --glob '*.py'
rg -n '"<name>"|__all__' "$REPO_ROOT"
```

同时检查 `__init__.py` re-export、测试、调用点和文档入口。

### 2. 提取签名和返回值

使用脚本：

```bash
python3 "$SKILL_DIR/scripts/extract_api.py" \
  path/to/file.py \
  --names vadd,vsub,vor
```

人工确认：

- 参数顺序、默认值、类型；
- 返回类型；
- tuple / pair / `None`；
- 是否 `@builtin`；
- 是否是普通 TileLang 函数。

### 3. 确认 AVE TD 和 lowering

```bash
rg -n 'def AVE_.*<op>|"<op>"' \
  "$REPO_ROOT/third_party/ascend/AscendNPU-IR/bishengir/include/bishengir/Dialect/HIVMAVE/IR/HIVMAVEOps.td"
```

再检查：

- intrinsic registry 实际 dtype；
- library-call fallback dtype；
- CCE stub overload；
- ODS 允许范围与实际 lowering 是否一致。

详细映射见 `reference/ave-td.md`。

### 4. 确认位宽 / lane / mask / mode

至少记录：

- 向量寄存器总位宽；
- 每种 dtype 的满 lane 数；
- mask 类型和 lane 数；
- 默认 mask 是否全 true；
- `MODE_ZEROING` / `MODE_MERGING` 实际行为；
- 是否需要 mutable destination；
- merging 是否有原生 overload；
- `mask=None` 时如何生成默认 `pset/pge`。

### 5. 生成评审文档

评审文档放在仓库外，避免误提交。推荐：

```bash
mkdir -p "${TMPDIR:-/tmp}/ascend-interface-review"
```

模板见 `reference/spec-template.md`。

必须列出：

- 已实现；
- 未实现；
- 仅底层支持但前端未开放；
- 不确定点；
- 待用户确认项。

### 6. 写 docstring

- TLA：`@builtin` + reST docstring。
- TileLang：普通函数 + reST docstring，内部调用 `tirx.call_intrin`。
- 普通 `#` 注释不会进入文档。

模板见 `reference/docstring-templates.md`。

规则：

- 使用 `:param:`、`:type:`、`:return:`、`:rtype:`。
- 代码名用双反引号。
- 注意事项用 `.. note::`。
- 不写未确认的 dtype 或行为。
- 不写用户未要求的业务边界。

### 7. 补 TA 自动文档入口

TLA 自动文档使用 Sphinx autosummary，不放在 programming guide。

文件：

```text
docs/zh/python-api/triton.language.extra.<module>.rst
```

模板见 `reference/docstring-templates.md`。

注意：

- `:orphan:` 页面不会出现在左侧导航。
- 需要导航可见时，再单独讨论是否加入 `docs/zh/index.rst`。

### 8. 构建与验证

使用 `reference/sphinx-workflow.md` 中的流程，或：

```bash
python3 "$SKILL_DIR/scripts/check_docstrings.py" path/to/file.py --names vadd,vsub
```

构建：

```bash
TORCH_DEVICE_BACKEND_AUTOLOAD=0 \
"$PYTHON" -m "$SPHINX_MODULE" -b html "$DOCS_DIR" "$DOCS_DIR/_build/html" -j auto
```

验证：

1. `python3 -m py_compile <changed.py>`
2. `git diff --check`
3. AST / `inspect.getdoc()` 能读到 docstring
4. Sphinx build 成功
5. 目标页面和 generated 页面存在
6. 页面不包含用户要求删除的内容
7. 文档导入的是源码树，不是旧 wheel

### 9. 清理与预览

先复制 HTML 到仓库外，再清理仓库内构建产物：

```bash
PREVIEW_DIR="${PREVIEW_DIR:-${TMPDIR:-/tmp}/ascend-interface-docs-preview}"
rm -rf "$PREVIEW_DIR"
mkdir -p "$PREVIEW_DIR"
cp -a "$DOCS_DIR/_build/html/." "$PREVIEW_DIR"/

rm -rf "$DOCS_DIR/_build" "$DOCS_DIR/python-api/generated"
```

启动预览：

```bash
python3 "$SKILL_DIR/scripts/build_preview.sh" --serve
```

停止：

```bash
python3 "$SKILL_DIR/scripts/stop_preview.sh"
```

页面是 `:orphan:` 时，必须直接访问 URL，不能只从首页导航找。

## 拆分文件

- `reference/spec-template.md`：评审规格文档模板
- `reference/docstring-templates.md`：TLA / TileLang / RST 模板
- `reference/ave-td.md`：AVE TD、lowering、CCE 映射与冲突处理
- `reference/sphinx-workflow.md`：Sphinx 构建、验证、预览
- `reference/pitfalls.md`：常见问题和排查
- `scripts/extract_api.py`：提取签名和 docstring
- `scripts/check_docstrings.py`：检查 docstring 完整性
- `scripts/build_preview.sh`：构建、复制、清理、预览
- `scripts/stop_preview.sh`：停止预览服务

## 输出检查清单

- [ ] 接口真实存在
- [ ] 签名、默认值、返回值已确认
- [ ] AVE TD 已查
- [ ] intrinsic / library-call / CCE overload 已查
- [ ] dtype / 位宽 / lane / mask / mode 已记录
- [ ] 不确定点已列出
- [ ] 用户未确认前没有修改代码
- [ ] docstring 使用 reST
- [ ] 未写未经确认的业务边界
- [ ] 自动文档 RST 使用 `:orphan:`
- [ ] Sphinx build 成功
- [ ] orphan 页面可直接访问
- [ ] 构建产物未提交
- [ ] `git status` 只包含预期文件
