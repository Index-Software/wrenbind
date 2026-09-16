//===----------------------------------------------------------------------===//
//
// Part of the wrenbind, under the MIT License.
// See LICENSE for license information.
// SPDX-License-Identifier: MIT
//
//===----------------------------------------------------------------------===//

#ifndef ARG_H
#define ARG_H

#pragma once

#ifdef __cplusplus
extern "C" {
#endif
#include "wren.h"
#ifdef __cplusplus
}
#endif
#include "platform.h"

template<typename T>
class CWrenBindArg
{
public:
	static T Get(WrenVM* pVm, int slot);
	static void Set(WrenVM* pVm, const T& val);
	static void SetAt(WrenVM* pVm, int slot, const T& val);
};

template<>
class CWrenBindArg<bool>
{
public:
	static bool Get(WrenVM* pVm, int slot)
	{
		return wrenGetSlotBool(pVm, slot);
	}

	static void Set(WrenVM* pVm, const bool& val)
	{
		wrenSetSlotBool(pVm, 0, val);
	}

	static void SetAt(WrenVM* pVm, int slot, const bool& val)
	{
		wrenSetSlotBool(pVm, slot, val);
	}
};

template<>
class CWrenBindArg<int8>
{
public:
	static int8 Get(WrenVM* pVm, int slot)
	{
		return static_cast<int8>(wrenGetSlotDouble(pVm, slot));
	}

	static void Set(WrenVM* pVm, const int8& val)
	{
		wrenSetSlotDouble(pVm, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVm, int slot, const int8& val)
	{
		wrenSetSlotDouble(pVm, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<int32>
{
public:
	static int32 Get(WrenVM* pVm, int slot)
	{
		return static_cast<int32>(wrenGetSlotDouble(pVm, slot));
	}

	static void Set(WrenVM* pVm, const int32& val)
	{
		wrenSetSlotDouble(pVm, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVm, int slot, const int32& val)
	{
		wrenSetSlotDouble(pVm, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<uint8>
{
public:
	static uint8 Get(WrenVM* pVm, int slot)
	{
		return static_cast<uint8>(wrenGetSlotDouble(pVm, slot));
	}

	static void Set(WrenVM* pVm, const uint8& val)
	{
		wrenSetSlotDouble(pVm, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVm, int slot, const uint8& val)
	{
		wrenSetSlotDouble(pVm, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<uint32>
{
public:
	static uint32 Get(WrenVM* pVm, int slot)
	{
		return static_cast<uint32>(wrenGetSlotDouble(pVm, slot));
	}

	static void Set(WrenVM* pVm, const uint32& val)
	{
		wrenSetSlotDouble(pVm, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVm, int slot, const uint32& val)
	{
		wrenSetSlotDouble(pVm, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<int64>
{
public:
	static int64 Get(WrenVM* pVm, int slot)
	{
		return static_cast<int64>(wrenGetSlotDouble(pVm, slot));
	}

	static void Set(WrenVM* pVm, const int64& val)
	{
		wrenSetSlotDouble(pVm, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVm, int slot, const int64& val)
	{
		wrenSetSlotDouble(pVm, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<uint64>
{
public:
	static uint64 Get(WrenVM* pVm, int slot)
	{
		return static_cast<uint64>(wrenGetSlotDouble(pVm, slot));
	}

	static void Set(WrenVM* pVm, const uint64& val)
	{
		wrenSetSlotDouble(pVm, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVm, int slot, const uint64& val)
	{
		wrenSetSlotDouble(pVm, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<float32>
{
public:
	static float32 Get(WrenVM* pVm, int slot)
	{
		return static_cast<float32>(wrenGetSlotDouble(pVm, slot));
	}

	static void Set(WrenVM* pVm, const float32& val)
	{
		wrenSetSlotDouble(pVm, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVm, int slot, const float32& val)
	{
		wrenSetSlotDouble(pVm, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<float64>
{
public:
	static float64 Get(WrenVM* pVm, int slot)
	{
		return static_cast<float64>(wrenGetSlotDouble(pVm, slot));
	}

	static void Set(WrenVM* pVm, const float64& val)
	{
		wrenSetSlotDouble(pVm, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVm, int slot, const float64& val)
	{
		wrenSetSlotDouble(pVm, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<const char*>
{
public:
	static const char* Get(WrenVM* pVm, int slot)
	{
		return wrenGetSlotString(pVm, slot);
	}

	static void Set(WrenVM* pVm, const char* const& val)
	{
		wrenSetSlotString(pVm, 0, val);
	}

	static void SetAt(WrenVM* pVm, int slot, const char* const& val)
	{
		wrenSetSlotString(pVm, slot, val);
	}
};

#endif // ARG_H