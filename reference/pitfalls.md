# Pitfalls

## Installed Wheel Is Stale

验证源码 docstring 时，优先使用源码树导入。  
如果导入到已安装 wheel，可能仍是旧文档。

检查：

```python
import triton.language.extra.tla.simd as s
print(s.__file__)
```

如果路径指向 site-packages，而不是仓库源码，说明导入错了。

## `@builtin` And Comments

- `@builtin` 使用 `functools.wraps`，保留 `__doc__`。
- `#` 普通注释不会进入文档。
- 必须使用三引号 docstring。

## TLA vs TileLang

- TLA：`@builtin` + reST docstring。
- TileLang：普通函数 + `tirx.call_intrin`。
- 不要把 TileLang 函数写成 TLA 的 `@builtin` 模板。

## Sphinx Build Fails

常见原因：

- `torch_npu` 自动加载失败：设置 `TORCH_DEVICE_BACKEND_AUTOLOAD=0`。
- 缺少 `myst_parser` / `sphinx_rtd_theme`。
- mock 模式下模块导入失败。
- 导入到了旧 wheel。

## Orphan Page Not In Navigation

`:orphan:` 页面不会出现在首页或左侧导航。  
必须直接访问生成页面 URL，或临时把页面加入 toctree。

## Cleanup Order

必须先复制 `_build/html` 到仓库外，再删除 `_build`。  
反向操作会导致预览内容丢失。

## Generated RST

`autosummary` 会在源码树生成 `python-api/generated/*.rst`。  
构建结束后清理，避免误提交。

## History Warnings

构建成功但可能有大量历史 warning。  
不要用 `-W` 直接失败；先记录 baseline，只关注新增 warning。

## Git Safety

写文档前检查：

```bash
git status --short
git diff --stat
git diff --check
```

未获用户明确要求不要 commit。  
只提交目标文件，不提交构建产物或无关修改。

## AVE / CCE Conflicts

AVE TD、intrinsic registry、library-call、CCE stub 可能不一致。  
不要把冲突写成单一结论，列入评审文档的不确定点。
