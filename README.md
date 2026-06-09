# wrenbind

### A Wren binding code generation framework for C++ projects.

wrenbind is a lightweight framework for binding C++ classes to the [Wren scripting language](https://wren.io/). It provides annotation macros for decorating C++ headers and a libclang-based Python code generator that produces the Wren foreign method forwarders, type serialization helpers, and binding registration tables automatically.

## Requirements

##### Core dependencies:

- [wren](https://github.com/wren-lang/wren)
- [libclang](https://llvm.org/) (Python `clang.cindex` for code generation)
- [`public/tier0/platform.h`](https://gist.github.com/rs189/0a5cd6dca531814218f2e31dab0556ca) (internal platform definitions)


## Interface

### BindingEntry_t
- `const char* m_ClassName`
- `const char* m_Signature`
- `WrenForeignMethodFn m_Function`
- `bool m_IsStatic`

### CWrenBindSingleton
- `static void Set(T* pInstance)`

### CWrenBindAllocator
- `static void* Alloc(size_t size)`
- `static void Free(void* pMemory)`

### CWrenBindArg
- `static T Get(WrenVM* pVm, int slot)`
- `static void Set(WrenVM* pVm, const T& val)`
- `static void SetAt(WrenVM* pVm, int slot, const T& val)`

## Usage

```cpp
#include "WrenBind.h"

#ifdef WREN_BIND_CODEGEN

class CMyClass
{
public:
    // Constructor
    WREN_CONSTRUCTOR("init new(_,_)")
    CMyClass(float32 x, float32 y);

    // Instance method
    WREN_BIND("moveBy(_,_)")
    void MoveBy(float32 dx, float32 dy);

    // Property getter mapped to a Wren field
    float32 GetX() const WREN_BIND("x=m_X");

    // Static method
    static float32 Distance(const CMyClass& a, const CMyClass& b) WREN_BIND_STATIC("distance(_,_)");

    // Operator overload
    bool operator==(const CMyClass&) const WREN_BIND("equals(_)");
};

#endif // WREN_BIND_CODEGEN
```

```bash
python3 scripts/generate_bindings.py \
    --input MyClass.h \
    --include include \
    --output MyClass.gen.cpp --header-output MyClass.gen.h
```

## License

wrenbind is licensed under the [MIT License](LICENSE).