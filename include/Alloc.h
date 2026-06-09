//===----------------------------------------------------------------------===//
//
// Part of the wrenbind, under the MIT License.
// See LICENSE for license information.
// SPDX-License-Identifier: MIT
//
//===----------------------------------------------------------------------===//

#ifndef ALLOC_H
#define ALLOC_H

#pragma once

#include <stddef.h>

template<typename T>
class CWrenBindAllocator
{
public:
	static void* Alloc(size_t size);
	static void Free(void* pMemory);
};

#endif // ALLOC_H