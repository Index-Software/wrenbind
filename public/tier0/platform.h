//===----------------------------------------------------------------------===//
//
// Part of the wrenbind, under the MIT License.
// See LICENSE for license information.
// SPDX-License-Identifier: MIT
//
//===----------------------------------------------------------------------===//

#ifndef WB_PLATFORM_H
#define WB_PLATFORM_H

#pragma once

#if defined(__cplusplus) && __cplusplus >= 201103L
	#define WB_MODERN_CPP 1
#endif

// NULL definition
#ifdef WB_MODERN_CPP
	#define WB_NULL nullptr
#else // WB_MODERN_CPP
	#define WB_NULL 0
#endif // !WB_MODERN_CPP

// Basic types
typedef signed char int8;
typedef unsigned char uint8;
typedef signed short int16;
typedef unsigned short uint16;
typedef signed int int32;
typedef unsigned int uint32;

#if defined( _MSC_VER )
	typedef signed __int64 int64;
	typedef unsigned __int64 uint64;
#else
	typedef signed long long int64;
	typedef unsigned long long uint64;
#endif // _MSC_VER

typedef float float32;
typedef double float64;

#endif // WB_PLATFORM_H