//===----------------------------------------------------------------------===//
//
// Part of the wrenbind, under the MIT License.
// See LICENSE for license information.
// SPDX-License-Identifier: MIT
//
//===----------------------------------------------------------------------===//

#ifndef WREN_HANDLE_H
#define WREN_HANDLE_H

#pragma once

#include "wren.hpp"
#include "../public/platform.h"

class CWrenHandle
{
public:
	CWrenHandle(WrenVM* pVm, WrenHandle* pHandle) :
		m_pVM(pVm),
		m_pHandle(pHandle)
	{
	}

	~CWrenHandle()
	{
		if (m_pHandle)
		{
			wrenReleaseHandle(m_pVM, m_pHandle);
		}
	}

	operator WrenHandle*() const
	{
		return m_pHandle;
	}

	// Returns the handle and stops owning it
	WrenHandle* Detach()
	{
		WrenHandle* pHandle = m_pHandle;
		m_pHandle = WB_NULL;

		return pHandle;
	}
private:
	CWrenHandle(const CWrenHandle&);
	CWrenHandle& operator=(const CWrenHandle&);

	WrenVM* m_pVM;
	WrenHandle* m_pHandle;
};

#endif // WREN_HANDLE_H