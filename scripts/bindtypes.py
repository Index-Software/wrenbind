import re
from typing import Callable, Optional


TYPE_READERS: dict[str, Callable[[int], tuple[str, int]]] = {
    "float64": (lambda s: (f"wrenGetSlotDouble(pVm, {s})", 1)),
    "float32": (
        lambda s: (f"static_cast<float32>(wrenGetSlotDouble(pVm, {s}))", 1)
    ),
    "int32": (
        lambda s: (f"static_cast<int32>(wrenGetSlotDouble(pVm, {s}))", 1)
    ),
    "uint32": (
        lambda s: (f"static_cast<uint32>(wrenGetSlotDouble(pVm, {s}))", 1)
    ),
    "int8": (
        lambda s: (f"static_cast<int8>(wrenGetSlotDouble(pVm, {s}))", 1)
    ),
    "uint8": (
        lambda s: (f"static_cast<uint8>(wrenGetSlotDouble(pVm, {s}))", 1)
    ),
    "int64": (
        lambda s: (f"static_cast<int64>(wrenGetSlotDouble(pVm, {s}))", 1)
    ),
    "uint64": (
        lambda s: (f"static_cast<uint64>(wrenGetSlotDouble(pVm, {s}))", 1)
    ),
    "bool": (lambda s: (f"wrenGetSlotBool(pVm, {s})", 1)),
    "const char *": (lambda s: (f"wrenGetSlotString(pVm, {s})", 1)),
}

TYPE_WRITERS: dict[str, Optional[str]] = {
    "void": None,
    "float64": "wrenSetSlotDouble(pVm, 0, {expr})",
    "bool": "wrenSetSlotBool(pVm, 0, {expr})",
    "float32": "wrenSetSlotDouble(pVm, 0, static_cast<float64>({expr}))",
    "int32": "wrenSetSlotDouble(pVm, 0, static_cast<float64>({expr}))",
    "uint32": "wrenSetSlotDouble(pVm, 0, static_cast<float64>({expr}))",
    "int8": "wrenSetSlotDouble(pVm, 0, static_cast<float64>({expr}))",
    "uint8": "wrenSetSlotDouble(pVm, 0, static_cast<float64>({expr}))",
    "int64": "wrenSetSlotDouble(pVm, 0, static_cast<float64>({expr}))",
    "uint64": "wrenSetSlotDouble(pVm, 0, static_cast<float64>({expr}))",
    "const char *": "wrenSetSlotString(pVm, 0, {expr})",
}

ENUM_WRITER: str = "wrenSetSlotDouble(pVm, 0, static_cast<float64>({expr}))"

MULTI_SLOT_TYPES: dict[str, int] = {
    "CVector4": 4,
}

KEYS_MULTI_SLOT: frozenset[str] = frozenset(MULTI_SLOT_TYPES.keys())


def normalize_type(raw_type: str) -> str:
    return raw_type.strip()


def is_builtin(ntype: str) -> bool:
    return ntype in TYPE_READERS


def get_builtin_reader(ntype: str, slot: int) -> tuple[str, int]:
    expr, slots = TYPE_READERS[ntype](slot)

    return (expr, slots)


def get_builtin_writer(ntype: str, expr: str) -> Optional[str]:
    template = TYPE_WRITERS.get(ntype)
    if template is None:
        return None

    return template.format(expr=expr)


def format_slot(expr: str, slot: int) -> str:
    return re.sub(
        r"\{slot(\+(\d+))?\}",
        lambda m: str(slot + int(m.group(2) or 0)),
        expr,
    )


def slot_count_for(ntype: str) -> int:
    return MULTI_SLOT_TYPES.get(ntype, 1)