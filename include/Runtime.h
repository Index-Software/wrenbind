//===----------------------------------------------------------------------===//
//
// Part of the wrenbind, under the MIT License.
// See LICENSE for license information.
// SPDX-License-Identifier: MIT
//
//===----------------------------------------------------------------------===//

#ifndef RUNTIME_H
#define RUNTIME_H

#pragma once

#include "wren.hpp"
#include "../public/tier0/platform.h"
#include "Handle.h"

struct BindingEntry_t
{
	const char* m_ClassName;
	const char* m_Signature;
	WrenForeignMethodFn m_Function;
	bool m_IsStatic;
};

#define BIND(cls, sig, func, isStatic) { cls, sig, func, isStatic }

// Reads the Handle_t stored in a foreign class slot
Handle_t GetForeign(WrenVM* pVm, int slot);

extern BindingEntry_t s_GeneratedBindings[];
extern const int s_NumGeneratedBindings;
extern WrenForeignClassMethods s_GeneratedClassMethods(
	WrenVM* pVm,
	const char* pModule,
	const char* pClassName
);

void WrenSetupConfig(WrenConfiguration* pConfig);

#endif // RUNTIME_H