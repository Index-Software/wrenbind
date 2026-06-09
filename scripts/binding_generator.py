from dataclasses import dataclass
import glob
import os
import re
import sys
from typing import Optional

import clang.cindex

from bindtypes import get_builtin_reader, get_builtin_writer, is_builtin, normalize_type


@dataclass
class Annotation:
    kind: str
    class_name: Optional[str]
    signature: str
    singleton: Optional[str] = None
    is_constructor: bool = False
    forwarder_fn: Optional[str] = None
    cxx_expr: Optional[str] = None
    var: Optional[str] = None


@dataclass
class Param:
    name: str
    type: str
    type_kind: clang.cindex.TypeKind
    type_canonical: str


@dataclass
class Singleton:
    type: str
    var: str
    file: str


@dataclass
class Method:
    class_name: str
    signature: str
    method_name: str
    params: list["Param"]
    is_constructor: bool
    return_type: str
    return_type_kind: Optional[clang.cindex.TypeKind]
    return_type_canonical: str
    cxx_expr: Optional[str] = None
    singleton: Optional[str] = None
    forwarder_fn: Optional[str] = None


def parse_annotation(text: str) -> Optional[Annotation]:
    if not text.startswith("wren:"):
        return None

    rest = text[5:]
    if not rest:
        return None

    parts = rest.split(":")
    kind = parts[0]

    class_name = None
    signature = ""
    singleton = None
    is_constructor = False
    forwarder_fn = None
    var = None

    if kind == "i":
        if len(parts) == 2:
            signature = parts[1]
        elif len(parts) >= 3:
            class_name = parts[1]
            signature = parts[2]
    elif kind == "s":
        if len(parts) == 3:
            signature = parts[1]
            singleton = parts[2]
        elif len(parts) >= 4:
            class_name = parts[1]
            signature = parts[2]
            singleton = parts[3]
    elif kind == "t":
        if len(parts) == 2:
            signature = parts[1]
        elif len(parts) >= 3:
            class_name = parts[1]
            signature = parts[2]
            singleton = f"::{parts[1]}"
    elif kind == "c":
        if len(parts) == 2:
            signature = parts[1]
            is_constructor = True
        elif len(parts) >= 3:
            class_name = parts[1]
            signature = parts[2]
            singleton = parts[3] if len(parts) >= 4 else None
            is_constructor = True
    elif kind == "g":
        var = parts[1] if len(parts) >= 2 else None
    elif kind == "f":
        if len(parts) == 3:
            signature = parts[1]
            forwarder_fn = parts[2]
        elif len(parts) >= 4:
            class_name = parts[1]
            signature = parts[2]
            forwarder_fn = parts[3]

    cxx_expr = None
    if kind != "f" and signature and "=" in signature:
        wren_sig, cxx_expr = signature.split("=", 1)
        signature = wren_sig
    elif kind == "f":
        pass

    return Annotation(
        kind=kind,
        class_name=class_name,
        signature=signature,
        singleton=singleton,
        is_constructor=is_constructor,
        forwarder_fn=forwarder_fn,
        cxx_expr=cxx_expr,
        var=var,
    )


def forwarder_name(m: Method) -> str:
    wren_method = m.signature.split("(")[0].replace(" ", "_")
    num_params = m.signature.count("_")

    return f"WrenBindForward_{m.class_name}_{wren_method}_{num_params}param"


def _strip_qualifiers(ntype: str) -> str:
    s = ntype
    if s.startswith("const "):
        s = s[6:]
    s = s.strip()
    while s.endswith(" &") or s.endswith(" *"):
        s = s.rstrip(" *&").strip()
    if s.startswith("class "):
        s = s[6:].strip()

    return s


class BindingGenerator:
    def __init__(
        self,
        wren_scripts_dir: Optional[str],
        include_dirs: list[str],
        libclang_path: Optional[str] = None,
    ) -> None:
        self._include_dirs = include_dirs
        self._foreign_class_map: dict[str, str] = {}
        self._scan_wren_scripts(wren_scripts_dir)

        self.all_methods: list[Method] = []
        self.seen_methods: set[tuple] = set()
        self._singletons: list[Singleton] = []
        self._seen_singletons: set[tuple[str, str]] = set()
        self._seen_classes: set[str] = set()
        self._input_files: list[str] = []
        if libclang_path:
            clang.cindex.Config.set_library_file(libclang_path)

    def _scan_wren_scripts(self, scripts_root: Optional[str]) -> None:
        if not scripts_root or not os.path.isdir(scripts_root):
            return
        print(f"Scanning Wren scripts in {scripts_root}...")
        pattern = os.path.join(scripts_root, "**", "*.wren")
        for fpath in glob.iglob(pattern, recursive=True):
            try:
                rel = os.path.relpath(fpath, scripts_root)
                module = rel.replace("\\", "/")
                if module.endswith(".wren"):
                    module = module[:-5]
                with open(fpath, "r") as fh:
                    for line in fh:
                        m = re.match(r"^\s*foreign\s+class\s+(\w+)", line)
                        if m:
                            cls_name = m.group(1)
                            self._foreign_class_map[cls_name] = module
            except OSError:
                pass
            except re.error:
                pass

    def _best_include_path(self, filepath: str) -> Optional[str]:
        best = None
        for d in self._include_dirs:
            try:
                rel = os.path.relpath(filepath, d)
                if not rel.startswith("..") and (
                    best is None or len(rel) < len(best)
                ):
                    best = rel
            except ValueError:
                pass

        return best

    def parse_files(self, input_files: list[str], include_args: list[str]) -> None:
        idx = clang.cindex.Index.create()
        self._input_files = input_files

        for filepath in input_files:
            print(f"Parsing {filepath}...")
            tu = idx.parse(filepath, args=include_args)
            errors = [d for d in tu.diagnostics if d.severity >= 4]
            for e in errors:
                print(
                    f"Error parsing {filepath}: {e.spelling}",
                    file=sys.stderr,
                )
                sys.exit(1)

            self._visit(tu.cursor)

    def _visit(self, cursor: clang.cindex.Cursor) -> None:
        if cursor.kind in (
            clang.cindex.CursorKind.CXX_METHOD,
            clang.cindex.CursorKind.CONSTRUCTOR,
        ):
            info_list: list[Annotation] = []
            for child in cursor.get_children():
                if child.kind == clang.cindex.CursorKind.ANNOTATE_ATTR:
                    info = parse_annotation(child.spelling)
                    if info:
                        info_list.append(info)

            for info in info_list:
                if info.class_name is None:
                    parent = cursor.semantic_parent
                    if parent and parent.kind in (
                        clang.cindex.CursorKind.CLASS_DECL,
                        clang.cindex.CursorKind.STRUCT_DECL,
                        clang.cindex.CursorKind.CLASS_TEMPLATE,
                    ):
                        info.class_name = parent.spelling
                        if info.kind == "t":
                            info.singleton = f"::{parent.spelling}"

                if info.kind == "g":
                    cls = info.class_name
                    if info.var:
                        var = info.var
                    else:
                        var = (
                            f"CWrenBindSingleton<{cls}>::s_pInstance"
                        )
                    key = (cls, var)
                    if key not in self._seen_singletons:
                        self._seen_singletons.add(key)
                        self._singletons.append(
                            Singleton(
                                type=cls,
                                var=var,
                                file=cursor.location.file.name,
                            )
                        )
                    continue

                if (
                    info.kind in ("s",)
                    and info.singleton
                    and not info.singleton.startswith("::")
                    and info.class_name
                ):
                    for s in self._singletons:
                        if s.type == info.class_name:
                            info.singleton = (
                                f"CWrenBindSingleton<"
                                f"{info.class_name}>::s_pInstance"
                            )
                            break

                params: list[Param] = []
                for p in cursor.get_children():
                    if p.kind == clang.cindex.CursorKind.PARM_DECL:
                        canonical = ""
                        try:
                            canonical = p.type.get_canonical().spelling
                        except AttributeError:
                            canonical = p.type.spelling
                        params.append(
                            Param(
                                name=p.spelling,
                                type=p.type.spelling,
                                type_kind=p.type.kind,
                                type_canonical=canonical,
                            )
                        )

                method_key = (
                    info.class_name,
                    cursor.spelling if not info.is_constructor else "ctor",
                    info.signature,
                )
                if method_key in self.seen_methods:
                    continue

                self.seen_methods.add(method_key)

                if info.is_constructor:
                    self._seen_classes.add(info.class_name)

                ret_canonical = ""
                ret_kind = None
                if not info.is_constructor:
                    try:
                        ret_canonical = (
                            cursor.result_type.get_canonical().spelling
                        )
                        ret_kind = cursor.result_type.kind
                    except AttributeError:
                        ret_canonical = cursor.result_type.spelling
                        ret_kind = cursor.result_type.kind

                if info.is_constructor:
                    ret_type = "void"
                else:
                    ret_type = cursor.result_type.spelling

                entry = Method(
                    class_name=info.class_name,
                    signature=info.signature,
                    method_name=cursor.spelling,
                    params=params,
                    is_constructor=info.is_constructor,
                    return_type=ret_type,
                    return_type_kind=ret_kind,
                    return_type_canonical=ret_canonical,
                    cxx_expr=info.cxx_expr,
                    singleton=info.singleton,
                    forwarder_fn=info.forwarder_fn,
                )
                self.all_methods.append(entry)

                if not info.is_constructor and not info.singleton:
                    self._seen_classes.add(info.class_name)

        for child in cursor.get_children():
            self._visit(child)

    def _singleton_var_for(self, base_type: str) -> Optional[str]:
        for s in self._singletons:
            if s.type == base_type:
                return s.var

        return None

    def _is_class_static(self, class_name: str) -> bool:
        for s in self._singletons:
            if s.type == class_name:
                return True

        for m in self.all_methods:
            if m.class_name == class_name and m.singleton:
                return True

        return False

    def _dispatch_read(
        self,
        ntype: str,
        type_spelling: str,
        type_kind: clang.cindex.TypeKind,
        type_canonical: str,
        slot: int,
    ) -> tuple[str, int]:
        if type_kind == clang.cindex.TypeKind.ENUM:
            return (
                f"static_cast<{type_spelling}>(static_cast<int32>("
                f"wrenGetSlotDouble(pVm, {slot})))",
                1,
            )

        collapsed = " ".join(ntype.split())
        if is_builtin(collapsed):
            return get_builtin_reader(collapsed, slot)

        if type_kind == clang.cindex.TypeKind.POINTER:
            base = _strip_qualifiers(ntype)
            svar = self._singleton_var_for(base)
            if svar:
                return (f"{svar}", 0)
            return (
                f"static_cast<{base}*>(HandleToPtr("
                f"*static_cast<Handle_t*>("
                f"wrenGetSlotForeign(pVm, {slot}))))",
                1,
            )

        if type_kind in (
            clang.cindex.TypeKind.LVALUEREFERENCE,
            clang.cindex.TypeKind.RVALUEREFERENCE,
        ):
            base = _strip_qualifiers(ntype)
            svar = self._singleton_var_for(base)
            if svar:
                return (f"( *{svar})", 0)
            return (
                f"( *static_cast<{base}*>(HandleToPtr("
                f"*static_cast<Handle_t*>("
                f"wrenGetSlotForeign(pVm, {slot})))))",
                1,
            )

        bare = _strip_qualifiers(ntype)
        result = f"CWrenBindArg<{bare}>::Get(pVm, {slot})".replace(
            ">>", "> >"
        )

        return (result, 1)

    def _dispatch_write(
        self,
        ntype: str,
        type_spelling: str,
        type_kind: clang.cindex.TypeKind,
        type_canonical: str,
        expr: str,
    ) -> str:
        if type_kind == clang.cindex.TypeKind.ENUM:
            return (
                f"wrenSetSlotDouble(pVm, 0, "
                f"static_cast<float64>({expr}))"
            )

        collapsed = " ".join(ntype.split())
        if is_builtin(collapsed):
            bw = get_builtin_writer(collapsed, expr)
            if bw is not None:
                return bw

        if type_kind == clang.cindex.TypeKind.POINTER:
            storage = " ".join(ntype.replace(">>", "> >").split())
            return (
                f"{storage} pRet = {expr}; "
                 f"if (pRet) wrenSetSlotDouble(pVm, 0, "
                f"static_cast<float64>(PtrToHandle("
                f"const_cast<void*>("
                f"reinterpret_cast<const void*>(pRet))))); "
                f"else wrenSetSlotNull(pVm, 0)"
            )

        bare = _strip_qualifiers(ntype)

        return f"CWrenBindArg<{bare}>::Set(pVm, {expr})".replace(">>", "> >")

    def _build_args(self, params: list["Param"]) -> list[str]:
        arg_exprs: list[str] = []
        slot = 1
        for p in params:
            ntype = normalize_type(p.type)
            expr, consumed = self._dispatch_read(
                ntype, p.type, p.type_kind, p.type_canonical, slot
            )
            arg_exprs.append(expr)
            slot += consumed

        return arg_exprs

    def generate(
        self,
        output_file: str,
        header_output_file: str,
        force_includes: Optional[list[str]] = None,
    ) -> None:
        print("Generating binding code...")
        lines: list[str] = []
        lines.append("//===----------------------------------------------------------------------===//")
        lines.append("//")
        lines.append("// Generated by wrenbind.")
        lines.append("// Do not edit.")
        lines.append("//")
        lines.append("//===----------------------------------------------------------------------===//")
        lines.append("")
        lines.append('#include "Runtime.h"')
        lines.append('#include "Handle.h"')
        lines.append('#include "Arg.h"')
        lines.append('#include "Alloc.h"')
        lines.append('#include <new>')
        lines.append('#include <string.h>')

        for inc in (force_includes or []):
            lines.append(f'#include "{inc}"')

        seen_inc: set[str] = set()
        for s in self._singletons:
            inc = self._best_include_path(s.file)
            if inc and inc not in seen_inc:
                seen_inc.add(inc)
                lines.append(f'#include "{inc}"')

        for f in self._input_files:
            rel = self._best_include_path(f)
            if rel and rel not in seen_inc:
                seen_inc.add(rel)
                lines.append(f'#include "{rel}"')

        fwd_funcs: list[str] = []
        seen_fwd: set[str] = set()
        for m in self.all_methods:
            fn = m.forwarder_fn
            if fn and fn not in seen_fwd:
                seen_fwd.add(fn)
                fwd_funcs.append(fn)
        if fwd_funcs:
            lines.append("")
            for fn in fwd_funcs:
                lines.append(f"extern void {fn}(WrenVM* pVm);")

        if not self.all_methods:
            lines.append(
                "BindingEntry_t s_GeneratedBindings[] = "
                '{ {"", "", WB_NULL, false} };',
            )
            lines.append("const int s_NumGeneratedBindings = 0;")
            lines.append(
                "WrenForeignClassMethods s_GeneratedClassMethods("
                "WrenVM* pVm, const char* pModule, "
                "const char* pClassName)",
            )
            lines.append("{")
            lines.append("\t(void)pVm; (void)pModule; (void)pClassName;")
            lines.append("\tWrenForeignClassMethods m = { 0, 0 };")
            lines.append("")
            lines.append("\treturn m;")
            lines.append("}")
            with open(output_file, "w") as f:
                f.write("\n".join(lines))
            print("[INFO] Generated empty bindings (no annotations found)")

            return

        for m in self.all_methods:
            cpp_class = m.class_name
            singleton = m.singleton
            func_name = forwarder_name(m)

            if cpp_class not in self._seen_classes:
                self._seen_classes.add(cpp_class)

            if m.forwarder_fn:
                continue

            if m.is_constructor:
                arg_exprs = self._build_args(m.params)
                lines.append("")
                lines.append(f"static void {func_name}(WrenVM* pVm)")
                lines.append("{")
                lines.append("\t(void)pVm;")
                lines.append(
                    f"\tvoid* pMem = CWrenBindAllocator<"
                    f"{cpp_class}>::Alloc(sizeof({cpp_class}));",
                )
                lines.append(
                    f"\t*static_cast<Handle_t*>("
                    f"wrenGetSlotForeign(pVm, 0)) = "
                    f"PtrToHandle(new(pMem) {cpp_class}("
                    f"{', '.join(arg_exprs)}));",
                )
                lines.append("}")
                continue

            if singleton:
                is_static_val = True
                if singleton.startswith("::"):
                    this_expr = singleton[2:]
                    use_colon_colon = True
                else:
                    this_expr = singleton
                    use_colon_colon = False
            else:
                this_expr = (
                    f"static_cast<{cpp_class}*>("
                    f"HandleToPtr(GetForeign(pVm, 0)))"
                )
                is_static_val = False
                use_colon_colon = False

            arg_exprs = self._build_args(m.params)
            sep = "::" if use_colon_colon else "->"
            if m.cxx_expr:
                call_expr = f"{this_expr}{sep}{m.cxx_expr}"
            else:
                call_expr = (
                    f"{this_expr}{sep}{m.method_name}("
                    f"{', '.join(arg_exprs)})"
                )

            lines.append("")
            lines.append(f"static void {func_name}(WrenVM* pVm)")

            return_writer = None
            ret = m.return_type if m.return_type else "void"
            if ret != "void":
                rntype = normalize_type(ret)
                return_writer = self._dispatch_write(
                    rntype,
                    ret,
                    m.return_type_kind,
                    m.return_type_canonical,
                    call_expr,
                )

            if return_writer is None:
                lines.append("{")
                lines.append(f"\t(void)pVm;")
                lines.append(f"\t{call_expr};")
                lines.append("}")
            else:
                lines.append("{")
                lines.append(f"\t{return_writer};")
                lines.append("}")

        foreign_classes: dict[str, str] = {}
        for m in self.all_methods:
            cls = m.class_name
            if cls in foreign_classes:
                continue

            is_owned = m.is_constructor
            foreign_classes[cls] = "owned" if is_owned else "borrowed"

        lines.append("")
        lines.append("BindingEntry_t s_GeneratedBindings[] =")
        lines.append("{")
        for m in self.all_methods:
            if m.forwarder_fn:
                fn_ref = m.forwarder_fn
            else:
                fn_ref = forwarder_name(m)
            if m.forwarder_fn and not m.singleton:
                is_static_str = (
                    "true"
                    if self._is_class_static(m.class_name)
                    else "false"
                )
            else:
                is_static_str = "true" if m.singleton else "false"
            lines.append(
                f'\tBIND("{m.class_name}", "{m.signature}", '
                f'{fn_ref}, {is_static_str}),',
            )
        lines.append("};")
        lines.append("")
        lines.append(
            "const int s_NumGeneratedBindings = "
            "sizeof(s_GeneratedBindings) / sizeof(s_GeneratedBindings[0]);",
        )

        if foreign_classes:
            lines.append("")
            for cls in sorted(foreign_classes):
                ftype = foreign_classes[cls]
                lines.append(f"static void s_Alloc_{cls}(WrenVM* pVm)")
                lines.append("{")
                lines.append(
                    "\twrenSetSlotNewForeign(pVm, 0, 0, sizeof(Handle_t));",
                )
                lines.append("}")
                lines.append("")
                if ftype == "owned":
                    lines.append(f"static void s_Fini_{cls}(void* pData)")
                    lines.append("{")
                    lines.append(
                        "\tHandle_t* pHandle = "
                        "static_cast<Handle_t*>(pData);",
                    )
                    lines.append("\tif (*pHandle)")
                    lines.append("\t{")
                    lines.append(
                        f"\t\t{cls}* p = static_cast<{cls}*>("
                        f"HandleToPtr(*pHandle));",
                    )
                    lines.append(
                        f"\t\tCWrenBindAllocator<{cls}>::Free(p);",
                    )
                    lines.append("\t}")
                    lines.append("}")
                else:
                    lines.append(f"static void s_Fini_{cls}(void* pData)")
                    lines.append("{")
                    lines.append(
                        f"\tHandle_t* pHandle = "
                        f"static_cast<Handle_t*>(pData);",
                    )
                    lines.append("\t(void)pHandle;")
                    lines.append("}")

                lines.append("")

        lines.append(
            "WrenForeignClassMethods s_GeneratedClassMethods("
            "WrenVM* pVm, const char* pModule, const char* pClassName)",
        )
        lines.append("{")
        lines.append("\t(void)pVm; (void)pModule;")
        lines.append("\tWrenForeignClassMethods methods = { 0, 0 };")
        for cls in sorted(foreign_classes):
            lines.append(f'\tif (strcmp(pClassName, "{cls}") == 0)')
            lines.append("\t{")
            lines.append(f"\t\tmethods.allocate = s_Alloc_{cls};")
            lines.append(f"\t\tmethods.finalize = s_Fini_{cls};")
            lines.append("")
            lines.append("\t\treturn methods;")
            lines.append("\t}")
        lines.append("")
        lines.append("\treturn methods;")
        lines.append("}")

        with open(output_file, "w") as f:
            f.write("\n".join(lines))
        print(
            f"[INFO] Generated {len(self.all_methods)} bindings "
            f"-> {output_file}",
        )

        hdr_lines: list[str] = []
        hdr_lines.append("//===----------------------------------------------------------------------===//")
        hdr_lines.append("//")
        hdr_lines.append("// Generated by wrenbind.")
        hdr_lines.append("// Do not edit.")
        hdr_lines.append("//")
        hdr_lines.append("//===----------------------------------------------------------------------===//")
        hdr_lines.append("")
        hdr_lines.append("#ifndef WREN_BIND_GENERATED_H")
        hdr_lines.append("#define WREN_BIND_GENERATED_H")
        hdr_lines.append("")
        hdr_lines.append("#pragma once")
        hdr_lines.append("")
        hdr_lines.append('#include "wren.h"')
        hdr_lines.append("")
        for s in self._singletons:
            hdr_lines.append(f"class {s.type};")
        hdr_lines.append("")
        hdr_lines.append("#endif // WREN_BIND_GENERATED_H")
        with open(header_output_file, "w") as f:
            f.write("\n".join(hdr_lines))
        print(
            f"[INFO] Generated header with forward declarations "
            f"-> {header_output_file}",
        )


def generate_empty_output(output_file: str) -> None:
    with open(output_file, "w") as f:
        f.write("//===----------------------------------------------------------------------===//\n")
        f.write("//\n")
        f.write("// Generated by wrenbind.\n")
        f.write("// Do not edit.\n")
        f.write("//\n")
        f.write("//===----------------------------------------------------------------------===//\n")
        f.write("\n")
        f.write(
            "BindingEntry_t s_GeneratedBindings[] = "
            '{ {"", "", WB_NULL, false} };\n',
        )
        f.write("const int s_NumGeneratedBindings = 0;\n")
        f.write(
            "WrenForeignClassMethods s_GeneratedClassMethods(\n"
            "\tWrenVM* pVm, const char* pModule, "
            "const char* pClassName)\n",
        )
        f.write("{\n")
        f.write("\t(void)pVm; (void)pModule; (void)pClassName;\n")
        f.write("\tWrenForeignClassMethods m = { 0, 0 };\n")
        f.write("\n\treturn m;\n")
        f.write("}\n")
    print("[INFO] Generated empty bindings (no annotations found)")