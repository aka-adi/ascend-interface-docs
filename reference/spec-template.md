# Interface Spec Review Template

用于接口规格评审稿。评审稿放在仓库外，例如：

```bash
REVIEW_DIR="${TMPDIR:-/tmp}/ascend-interface-review"
mkdir -p "$REVIEW_DIR"
```

## 文档头部

```markdown
# <topic> 接口规格（评审稿）

> 状态：评审稿，暂不写入代码
> 来源仓库：<repo>
> 来源提交：<commit>
> 参考实现：
>   - <Python source>
>   - <AVE TD>
>   - <CANN CCE stub>
>   - <tests>
```

## 1. 结论概览

```markdown
| 类别 | 已实现 | 未实现 | 仅底层支持 |
|---|---|---|---|
| <group> | ... | ... | ... |
```

必须明确：

- 哪些接口真实存在；
- 哪些只是底层有 overload，前端未开放；
- 哪些完全未实现；
- 哪些需要用户确认后才能写入代码。

## 2. 公共模型

记录：

- 向量寄存器总位宽；
- 每种 dtype 的 lane 数；
- mask 类型；
- 默认 mask；
- mode 枚举；
- dtype 命名；
- 是否要求特定 scope（如 SimdVF）。

## 3. 接口规格

推荐表头：

```markdown
| 接口 | 签名 | 语义 | dtype | 返回 | 约束 |
|---|---|---|---|---|---|
```

dtype 表必须区分：

- AVE TD 允许；
- intrinsic registry 支持；
- library-call fallback；
- CCE stub overload；
- Python 前端可接受。

## 4. AVE TD 复核

```markdown
| 接口 | AVE TD | TD/lowering 结论 |
|---|---|---|
```

冲突写法：

```text
AVE TD: ...
CCE stub: ...
结论：待确认
```

不要自行选一个事实来源。

## 5. 不确定点

每项使用 `U1`, `U2` 编号，至少覆盖：

- AVE TD 与 CCE stub dtype 冲突；
- Python 前端未校验的 dtype/scalar 类型；
- i64 lane 与 2xVL 表示；
- `MODE_MERGING` 是否正式支持；
- reduction 结果 lane 布局；
- store 的 stride/对齐/越界规则；
- event ID / flag ID / pipe 白名单；
- 目标架构差异；
- 使用作用域。

## 6. 待确认项

列出需要用户决策的问题，不要直接写实现方案。

## 7. 写入代码前检查

- [ ] 用户已确认规格
- [ ] 不确定点已关闭或明确保留
- [ ] 只修改目标 docstring
- [ ] 不修改运行时逻辑
- [ ] 不提交构建产物
