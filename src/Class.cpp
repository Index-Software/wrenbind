//===----------------------------------------------------------------------===//
//
// Part of the wrenbind, under the MIT License.
// See LICENSE for license information.
// SPDX-License-Identifier: MIT
//
//===----------------------------------------------------------------------===//

#include "Class.h"
#include "../public/dbg.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

CWrenBindClass::CWrenBindClass(const char* pModule, const char* pClassName) :
	m_pModule(pModule),
	m_pClassName(pClassName),
	m_pVM(WB_NULL),
	m_pHandle(WB_NULL)
{
}

void CWrenBindClass::Find(WrenVM* pVm)
{
	m_pVM = pVm;
	m_pHandle = WB_NULL;

	if (!wrenHasModule(pVm, m_pModule) ||
		!wrenHasVariable(pVm, m_pModule, m_pClassName))
	{
		Error("[Wren] Class not found: %s.%s\n", m_pModule, m_pClassName);

		return;
	}

	wrenEnsureSlots(pVm, 1);
	wrenGetVariable(pVm, m_pModule, m_pClassName, 0);

	// A handle is a GC root, so the class cannot be collected
	m_pHandle = wrenGetSlotHandle(pVm, 0);
}

WrenHandle* CWrenBindClass::Get(WrenVM* pVm)
{
	if (m_pVM == WB_NULL)
	{
		Find(pVm);
	}
	else
	{
		AssertMsg(pVm == m_pVM, "CWrenBindClass used with another VM");
	}

	return m_pHandle;
}

static bool s_ImportClasses(WrenVM* pVm)
{
	size_t length = 1;
	for (int i = 0; i < CWrenBind::s_NumGeneratedClasses; i++)
	{
		length += strlen(CWrenBind::s_GeneratedClasses[i]->Module()) +
			strlen(CWrenBind::s_GeneratedClasses[i]->Name()) + 16;
	}

	char* pSource = static_cast<char*>(malloc(length));
	if (!pSource)
	{
		return false;
	}

	pSource[0] = '\0';
	for (int i = 0; i < CWrenBind::s_NumGeneratedClasses; i++)
	{
		size_t used = strlen(pSource);
		snprintf(
			pSource + used,
			length - used,
			"import \"%s\" for %s\n",
			CWrenBind::s_GeneratedClasses[i]->Module(),
			CWrenBind::s_GeneratedClasses[i]->Name());
	}

	WrenInterpretResult result = wrenInterpret(
		pVm,
		"wrenbind/classes",
		pSource);
	free(pSource);

	if (result != WREN_RESULT_SUCCESS)
	{
		Error("[Wren] Failed to load the classes of the bindings\n");

		return false;
	}

	return true;
}

static bool s_FindClasses(WrenVM* pVm)
{
	for (int i = 0; i < CWrenBind::s_NumGeneratedClasses; i++)
	{
		if (!CWrenBind::s_GeneratedClasses[i]->Get(pVm))
		{
			return false;
		}
	}

	return true;
}

bool CWrenBind::Init(WrenVM* pVm)
{
	RegisterClasses();

	if (!s_ImportClasses(pVm))
	{
		return false;
	}

	return s_FindClasses(pVm);
}