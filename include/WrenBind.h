//===----------------------------------------------------------------------===//
//
// Part of the wrenbind, under the MIT License.
// See LICENSE for license information.
// SPDX-License-Identifier: MIT
//
//===----------------------------------------------------------------------===//

#ifndef WREN_BIND_H
#define WREN_BIND_H

#pragma once

#include "../public/tier0/platform.h"

template<typename T>
class CWrenBindSingleton
{
public:
	static T* s_pInstance;

	static void Set(T* pInstance)
	{
		s_pInstance = pInstance;
	}
};

template<typename T>
T* CWrenBindSingleton<T>::s_pInstance = WB_NULL;

#if defined(WREN_BIND_CODEGEN) && defined(__GNUC__)
#define WREN_BIND(sig) __attribute__((annotate("wren:i:" sig)))
#define WREN_BIND_SINGLETON(sig, var) __attribute__((annotate("wren:s:" sig ":" #var)))
#define WREN_BIND_STATIC(sig) __attribute__((annotate("wren:t:" sig)))
#define WREN_CONSTRUCTOR(sig) __attribute__((annotate("wren:c:" sig)))
#define WREN_CONSTRUCTOR_GLOBAL(sig, var) __attribute__((annotate("wren:c:" sig ":" #var)))
#define WREN_SINGLETON_DECL() __attribute__((annotate("wren:g"))) void __wren_singleton();
#define WREN_BIND_FWD(sig, fn) __attribute__((annotate("wren:f:" sig ":" fn)))
#else // !(WREN_BIND_CODEGEN && __GNUC__)
#define WREN_BIND(sig)
#define WREN_BIND_SINGLETON(sig, var)
#define WREN_BIND_STATIC(sig)
#define WREN_CONSTRUCTOR(sig)
#define WREN_CONSTRUCTOR_GLOBAL(sig, var)
#define WREN_SINGLETON_DECL()
#define WREN_BIND_FWD(sig, fn)
#endif // !(WREN_BIND_CODEGEN && __GNUC__)

#define WREN_SET_SINGLETON(Type, pVar) CWrenBindSingleton<Type>::Set(pVar)

#endif // WREN_BIND_H