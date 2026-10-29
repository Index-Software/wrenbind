//===----------------------------------------------------------------------===//
//
// Part of the wrenbind, under the MIT License.
// See LICENSE for license information.
// SPDX-License-Identifier: MIT
//
//===----------------------------------------------------------------------===//

#include "Runtime.h"
#include "../public/platform.h"
#include "../public/dbg.h"
#include <string.h>

Handle_t GetForeign(WrenVM* pVm, int slot)
{
	void* pData = wrenGetSlotForeign(pVm, slot);
	if (!pData)
	{
		return WB_NULL;
	}

	return *static_cast<Handle_t*>(pData);
}

static void s_WriteFn(WrenVM* pVm, const char* pText)
{
	Msg("%s\n", pText);
}

static void s_ErrorFn(
	WrenVM* pVm,
	WrenErrorType type,
	const char* pModule,
	int line,
	const char* pMessage)
{
	switch (type)
	{
	case WREN_ERROR_COMPILE:
		Error("[CWrenBind] Compile error in %s line %d: %s\n",
			pModule ? pModule : "?",
			line,
			pMessage);

		break;
	case WREN_ERROR_RUNTIME:
		Error("[CWrenBind] Runtime error: %s\n", pMessage);

		break;
	case WREN_ERROR_STACK_TRACE:
		Error("[CWrenBind] Stack trace %s line %d: %s\n",
			pModule ? pModule : "?",
			line,
			pMessage);

		break;
	}
}

static WrenForeignMethodFn s_BindMethodFn(
	WrenVM* pVm,
	const char* pModule,
	const char* pClassName,
	bool isStatic,
	const char* pSignature)
{
	for (int32 i = 0; i < s_NumGeneratedBindings; i++)
	{
		if (strcmp(s_GeneratedBindings[i].m_ClassName, pClassName) == 0 &&
			s_GeneratedBindings[i].m_IsStatic == isStatic &&
			strcmp(s_GeneratedBindings[i].m_Signature, pSignature) == 0)
		{
			return s_GeneratedBindings[i].m_Function;
		}
	}

	Error("[CWrenBind] Unbound method: %s.%s%s %s\n",
		pModule,
		pClassName,
		isStatic ? ".static" : "",
		pSignature);

	return WB_NULL;
}

static WrenForeignClassMethods s_BindClassFn(
	WrenVM* pVm,
	const char* pModule,
	const char* pClassName)
{
	return s_GeneratedClassMethods(pVm, pModule, pClassName);
}

void WrenSetupConfig(WrenConfiguration* pConfig)
{
	pConfig->writeFn = s_WriteFn;
	pConfig->errorFn = s_ErrorFn;
	pConfig->bindForeignClassFn = s_BindClassFn;
	pConfig->bindForeignMethodFn = s_BindMethodFn;
}