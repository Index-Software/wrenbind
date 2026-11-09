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
#endif // __cplusplus
#include "wren.h"
#ifdef __cplusplus
}
#endif // __cplusplus
#include "../public/platform.h"

template<typename T>
class CWrenBindArg
{
public:
	static T Get(WrenVM* pVM, int slot);
	static void Set(WrenVM* pVM, const T& val);
	static void SetAt(WrenVM* pVM, int slot, const T& val);
};

template<>
class CWrenBindArg<bool>
{
public:
	static bool Get(WrenVM* pVM, int slot)
	{
		return wrenGetSlotBool(pVM, slot);
	}

	static void Set(WrenVM* pVM, const bool& val)
	{
		wrenSetSlotBool(pVM, 0, val);
	}

	static void SetAt(WrenVM* pVM, int slot, const bool& val)
	{
		wrenSetSlotBool(pVM, slot, val);
	}
};

template<>
class CWrenBindArg<int8>
{
public:
	static int8 Get(WrenVM* pVM, int slot)
	{
		return static_cast<int8>(wrenGetSlotDouble(pVM, slot));
	}

	static void Set(WrenVM* pVM, const int8& val)
	{
		wrenSetSlotDouble(pVM, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVM, int slot, const int8& val)
	{
		wrenSetSlotDouble(pVM, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<int32>
{
public:
	static int32 Get(WrenVM* pVM, int slot)
	{
		return static_cast<int32>(wrenGetSlotDouble(pVM, slot));
	}

	static void Set(WrenVM* pVM, const int32& val)
	{
		wrenSetSlotDouble(pVM, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVM, int slot, const int32& val)
	{
		wrenSetSlotDouble(pVM, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<uint8>
{
public:
	static uint8 Get(WrenVM* pVM, int slot)
	{
		return static_cast<uint8>(wrenGetSlotDouble(pVM, slot));
	}

	static void Set(WrenVM* pVM, const uint8& val)
	{
		wrenSetSlotDouble(pVM, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVM, int slot, const uint8& val)
	{
		wrenSetSlotDouble(pVM, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<uint32>
{
public:
	static uint32 Get(WrenVM* pVM, int slot)
	{
		return static_cast<uint32>(wrenGetSlotDouble(pVM, slot));
	}

	static void Set(WrenVM* pVM, const uint32& val)
	{
		wrenSetSlotDouble(pVM, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVM, int slot, const uint32& val)
	{
		wrenSetSlotDouble(pVM, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<int64>
{
public:
	static int64 Get(WrenVM* pVM, int slot)
	{
		return static_cast<int64>(wrenGetSlotDouble(pVM, slot));
	}

	static void Set(WrenVM* pVM, const int64& val)
	{
		wrenSetSlotDouble(pVM, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVM, int slot, const int64& val)
	{
		wrenSetSlotDouble(pVM, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<uint64>
{
public:
	static uint64 Get(WrenVM* pVM, int slot)
	{
		return static_cast<uint64>(wrenGetSlotDouble(pVM, slot));
	}

	static void Set(WrenVM* pVM, const uint64& val)
	{
		wrenSetSlotDouble(pVM, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVM, int slot, const uint64& val)
	{
		wrenSetSlotDouble(pVM, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<float32>
{
public:
	static float32 Get(WrenVM* pVM, int slot)
	{
		return static_cast<float32>(wrenGetSlotDouble(pVM, slot));
	}

	static void Set(WrenVM* pVM, const float32& val)
	{
		wrenSetSlotDouble(pVM, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVM, int slot, const float32& val)
	{
		wrenSetSlotDouble(pVM, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<float64>
{
public:
	static float64 Get(WrenVM* pVM, int slot)
	{
		return static_cast<float64>(wrenGetSlotDouble(pVM, slot));
	}

	static void Set(WrenVM* pVM, const float64& val)
	{
		wrenSetSlotDouble(pVM, 0, static_cast<float64>(val));
	}

	static void SetAt(WrenVM* pVM, int slot, const float64& val)
	{
		wrenSetSlotDouble(pVM, slot, static_cast<float64>(val));
	}
};

template<>
class CWrenBindArg<const char*>
{
public:
	static const char* Get(WrenVM* pVM, int slot)
	{
		return wrenGetSlotString(pVM, slot);
	}

	static void Set(WrenVM* pVM, const char* const& val)
	{
		wrenSetSlotString(pVM, 0, val);
	}

	static void SetAt(WrenVM* pVM, int slot, const char* const& val)
	{
		wrenSetSlotString(pVM, slot, val);
	}
};

#endif // ARG_H