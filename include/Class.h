//===----------------------------------------------------------------------===//
//
// Part of the wrenbind, under the MIT License.
// See LICENSE for license information.
// SPDX-License-Identifier: MIT
//
//===----------------------------------------------------------------------===//

#ifndef CLASS_H
#define CLASS_H

#pragma once

#include "wren.hpp"
#include "../public/platform.h"

class CWrenBindClass
{
public:
	CWrenBindClass(const char* pModule, const char* pClassName);

	WrenHandle* Get(WrenVM* pVm);

	const char* Module() const
	{
		return m_pModule;
	}

	const char* Name() const
	{
		return m_pClassName;
	}
private:
	CWrenBindClass(const CWrenBindClass&);
	CWrenBindClass& operator=(const CWrenBindClass&);

	void Find(WrenVM* pVm);

	const char* m_pModule;
	const char* m_pClassName;
	WrenVM* m_pVM;
	WrenHandle* m_pHandle;
};

template<typename T>
struct CWrenBindClassOf
{
	static CWrenBindClass* s_pClass;

	static WrenHandle* Get(WrenVM* pVm)
	{
		return s_pClass ? s_pClass->Get(pVm) : WB_NULL;
	}
};

template<typename T>
CWrenBindClass* CWrenBindClassOf<T>::s_pClass = WB_NULL;

class CWrenBind
{
public:
	static bool Init(WrenVM* pVm);

	static void RegisterClasses();

	static CWrenBindClass* const s_GeneratedClasses[];
	static const int s_NumGeneratedClasses;
};

#endif // CLASS_H