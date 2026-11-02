# Sphinx Build And Preview

## Environment

```bash
REPO_ROOT=${REPO_ROOT:-$(git rev-parse --show-toplevel)}
DOCS_DIR=${DOCS_DIR:-$REPO_ROOT/docs/zh}
PYTHON=${PYTHON:-python3}
SPHINX_MODULE=${SPHINX_MODULE:-sphinx}
SKILL_DIR=${SKILL_DIR:-/path/to/skills/ascend-interface-docs}
PREVIEW_DIR=${PREVIEW_DIR:-${TMPDIR:-/tmp}/ascend-interface-docs-preview}
PORT=${PORT:-8766}
BIND=${BIND:-127.0.0.1}
```

如需临时安装依赖：

```bash
"$PYTHON" -m pip install sphinx sphinx_rtd_theme myst_parser
```

## Build

```bash
cd "$DOCS_DIR"
TORCH_DEVICE_BACKEND_AUTOLOAD=0 \
"$PYTHON" -m "$SPHINX_MODULE" -b html . _build/html -j auto
```

不建议直接用 `-W`：

- 仓库可能有大量历史 warning；
- 先确认 baseline；
- 只把本次新增 warning 当成回归。

## Verify

1. `python3 -m py_compile <changed.py>`
2. `git diff --check`
3. docstring 能通过 AST / `inspect.getdoc()` 读取
4. Sphinx build 成功
5. 目标页面存在：
   - `docs/zh/_build/html/python-api/<page>.html`
   - `docs/zh/_build/html/python-api/generated/<module>.<op>.html`
6. 页面不包含应删除内容
7. 导入路径指向源码树，不是旧 wheel

检查导入路径：

```python
import triton.language.extra.tla.simd as s
print(s.__file__)
```

## Copy And Clean

先复制，再清理：

```bash
rm -rf "$PREVIEW_DIR"
mkdir -p "$PREVIEW_DIR"
cp -a "$DOCS_DIR/_build/html/." "$PREVIEW_DIR"/

rm -rf "$DOCS_DIR/_build" "$DOCS_DIR/python-api/generated"
```

## Serve

```bash
python3 "$SKILL_DIR/scripts/build_preview.sh" --serve
```

或手动：

```bash
mkdir -p "${TMPDIR:-/tmp}/ascend-interface-docs-preview"
nohup python3 -m http.server "$PORT" --bind "$BIND" \
  --directory "$PREVIEW_DIR" \
  > "${TMPDIR:-/tmp}/ascend-interface-docs-server.log" 2>&1 &
echo $! > "${TMPDIR:-/tmp}/ascend-interface-docs-server.pid"
```

默认只绑定 `127.0.0.1`。需要局域网访问时显式设置 `BIND=0.0.0.0`。

停止：

```bash
python3 "$SKILL_DIR/scripts/stop_preview.sh"
```

## Orphan Pages

`:orphan:` 页面可以构建，但不会出现在左侧导航。必须直接访问 URL，例如：

```text
http://127.0.0.1:8766/python-api/triton.language.extra.tla.simd.html
```

如果希望进入导航，需要单独讨论是否加入 `docs/zh/index.rst` toctree。
