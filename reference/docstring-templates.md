# Docstring And Autosummary Templates

## TLA `@builtin`

```python
@builtin
def op(x, y, mask=None, mode=MODE.ZEROING, _semantic=None):
    """
    One-line summary (``ave.hir.op``).

    Semantics, dtype, bit width, lane count, mask and mode constraints.
    No implicit broadcast or dtype conversion.

    :param x: First vector register.
    :type x: tla.vector
    :param y: Second vector register with the same dtype and lane count.
    :type y: tla.vector
    :param mask: Optional predicate with one ``i1`` lane per data lane.
        ``None`` means an all-true mask.
    :type mask: tla.vector or None
    :param mode: Predication mode. ``MODE_ZEROING`` is the conservative
        supported mode; ``MODE_MERGING`` behavior must be confirmed.
    :type mode: tla.simd.MODE
    :return: Vector with the same dtype and lane count as the inputs.
    :rtype: tla.vector

    .. note::
        Conservative delivery scope and known limitations.
    """
```

## TileLang `T.simd.*` / `T.ascend_*`

TileLang Ascend API 通常是普通 Python 函数：

```python
def vadd(src0, src1, mask=None, mode="MODE_ZEROING"):
    """
    Element-wise vector add.

    :param src0: First vector register.
    :type src0: Vector value
    :param src1: Second vector register with the same dtype and lane count.
    :type src1: Vector value
    :param mask: Optional predicate; ``None`` selects the default all-lane mask.
    :type mask: Predicate vector or None
    :param mode: ``"MODE_ZEROING"`` or ``"MODE_MERGING"``.
    :type mode: str
    :return: Vector with the same dtype and lane count as the inputs.
    :rtype: Vector value
    """
    return tirx.call_intrin(...)
```

不要给 TileLang 函数加 TLA 的 `@builtin`。

## Sphinx autosummary RST

```rst
:orphan:

triton.language.extra.tla.simd
===============================

.. currentmodule:: triton.language.extra.tla.simd

Vector Ops
----------

.. autosummary::
    :toctree: generated
    :nosignatures:

    vadd
    vsub
```

规则：

- 文件名与模块路径一致。
- `:orphan:` 页面不会出现在左侧导航。
- 不在 programming guide 中新增接口文档。
- 需要导航可见时，单独讨论 `docs/zh/index.rst` toctree。
