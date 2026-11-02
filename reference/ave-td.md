# AVE TD And Lowering Verification

## Paths

```bash
REPO_ROOT=${REPO_ROOT:-$(git rev-parse --show-toplevel)}
CANN_ROOT=${CANN_ROOT:?set CANN_ROOT to the CANN installation root}

AVE_TD="$REPO_ROOT/third_party/ascend/AscendNPU-IR/bishengir/include/bishengir/Dialect/HIVMAVE/IR/HIVMAVEOps.td"
AVE_TYPES="$REPO_ROOT/third_party/ascend/AscendNPU-IR/bishengir/include/bishengir/Dialect/HIVMAVE/IR/HIVMAVETypes.td"
AVE_INTRIN="$REPO_ROOT/third_party/ascend/AscendNPU-IR/bishengir/lib/Conversion/HIVMAVEToAVEIntrin/HIVMAVEToAVEIntrin.cpp"
AVE_LIB="$REPO_ROOT/third_party/ascend/AscendNPU-IR/bishengir/lib/Conversion/HIVMAVEToStandard/HIVMAVEToStandard.cpp"
CCE_STUB="$CANN_ROOT/tools/cpudebug/include/stub_fun.h"
```

## Lookup

```bash
rg -n 'def AVE_.*<op>|"<op>"' "$AVE_TD"
rg -n '<op>|BinaryRegistry|BinaryVectorScalarRegistry' "$AVE_INTRIN"
rg -n '<op>|AVEOpToLibraryCallPattern' "$AVE_LIB"
rg -n 'void <op>\(' "$CCE_STUB"
```

## Contract Layers

按以下层次记录，不要混成一张 dtype 表：

1. **用户确认规格**：最终产品决策。
2. **Python frontend**：API 签名、默认值、是否提前校验。
3. **AVE TD ODS**：语义定义和形式允许范围。
4. **AVE intrinsic registry**：实际单寄存器 lowering。
5. **AVE library-call fallback**：i64 等特殊路径。
6. **CCE stub overload**：最终 C++ 编译可用范围。
7. **测试/示例**：已验证行为，只作为证据。

### 优先级

- **语义优先级**：
  `用户确认 > AVE TD > lowering > CCE intrinsic > 测试`
- **可用性优先级**：
  `用户确认 > Python 前端可调用 > AVE intrinsic > library-call > CCE stub > 测试`
- **正式 dtype 契约**：
  `Python 前端可接受 ∩ AVE intrinsic/library-call ∩ CCE stub`

冲突时写：

```text
AVE TD: ...
CCE stub: ...
Python frontend: ...
结论：待确认
```

## Common AVE Shapes

```text
AVE_BinaryOp
  - vadd/vsub/vmul/vmax/vmin/vor/vxor
  - operands/results are AveExtValidVector

AVE_VecScalarOp
  - vadds/vmaxs/vmins
  - scalar list is I8/I16/I32/I64/F16/F32

AVE_ReductionOp
  - kind: add/min/max/xori/umin/umax
  - result is placed at the first vector position (lane 0)

AVE_VFStoreWithStrideOp
  - value: I8/I16/I32/BF16/F16/F32/F8E4M3FN/F8E5M2
  - stride: Index

AVE_VFCmpOp
  - operands: AveExtValidVector
  - result: AveMaskType
```

## Typical Conflicts

- AVE TD 允许 float `vxor`，但 CCE stub 可能只有整数 overload。
- AVE TD 的 `vdiv` 可能排除 i8/u8/bf16，但 CCE stub 可能有更多 overload。
- AVE `VecScalarOp` 可能不支持 BF16 scalar，但 CCE stub 可能支持。
- i64 在 AVE 中可能是 4096-bit 特例，不能按 2048-bit 计算 lane。
- `vaddc`、部分 cross-lane reduction 可能没有 AVE TD，只能由 CCE 确认。

这些冲突必须进入评审文档的不确定点清单。
