# wrenbind

### A Wren binding code generation framework for C++ projects.

wrenbind is a lightweight framework for binding C++ classes to the [Wren scripting language](https://wren.io/). It provides annotation macros for decorating C++ headers and a libclang-based Python code generator that produces the Wren foreign method forwarders, type serialization helpers, and binding registration tables automatically.

## Requirements

##### Core dependencies:

- [wren](https://github.com/wren-lang/wren)
- [libclang](https://llvm.org/) (Python `clang.cindex` for code generation)
- [`public/platform.h`](public/platform.h) (internal platform definitions)

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

A process-wide object can be exposed as a singleton:

```cpp
class CMyClass
{
public:
    WREN_SINGLETON_DECL()

    CMyObject CreateObject() WREN_BIND_SINGLETON("createObject()", s_pMyClass);

    // Use a forwarder when the generator cannot express the call
    void AddComponent(uint32 id, CMyComponent* pComp)
        WREN_BIND_FWD("addComponent(_,_)", "WrenFwd_CMyClass_AddComponent");
};
```

Set the instance once, after the VM is created:

```cpp
WREN_SET_SINGLETON(CMyClass, pMyClass);
```

```bash
python3 wrenbind/generate_bindings.py \
    --input MyClass.h \
    --include include \
    --output MyClass.gen.cpp --header-output MyClass.gen.h
```

## License

wrenbind is licensed under the [MIT License](LICENSE).