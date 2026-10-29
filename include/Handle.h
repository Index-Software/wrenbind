//===----------------------------------------------------------------------===//
//
// Part of the wrenbind, under the MIT License.
// See LICENSE for license information.
// SPDX-License-Identifier: MIT
//
//===----------------------------------------------------------------------===//

#ifndef HANDLE_H
#define HANDLE_H

#pragma once

#include "../public/platform.h"

typedef uintp Handle_t;

static inline Handle_t PtrToHandle(void* pPtr)
{
	return reinterpret_cast<Handle_t>(pPtr);
}

static inline void* HandleToPtr(Handle_t hHandle)
{
	return reinterpret_cast<void*>(hHandle);
}

#endif // HANDLE_H