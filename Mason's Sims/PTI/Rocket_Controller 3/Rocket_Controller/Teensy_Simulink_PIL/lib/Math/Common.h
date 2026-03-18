#pragma once

// Common.h

// The purpose of this file is to improve the overall sanity of the other code
// by making compilers behave

#include <string>
#include <time.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>

#ifndef __PX4_NUTTX
#include <sys/timeb.h>
#endif

#ifndef _WIN32
// not technically 100% correct, but lets us move on with our lives
#define sprintf_s snprintf
#define vsprintf_s vsnprintf
#else
#ifndef _SCL_SECURE_NO_WARNINGS
#define _SCL_SECURE_NO_WARNINGS
#endif
#pragma warning(disable: 4996) //strcpy unsafe
#endif

#include <stdint.h>
#include <inttypes.h>
#include <unistd.h>
inline void Sleep(int msec)
{
  usleep(msec*1000);
}

#include <memory>
#include <functional>
using std::shared_ptr;
using std::weak_ptr;
using std::placeholders::_1;

#ifndef __PX4_NUTTX
#include <cmath>
inline bool _isnan(const double& v){return std::isnan(v);}
inline bool _isnan(const float& v){return std::isnan(v);}
#endif

#include "Constants.h"
#include "V3F.h"
#include "V3D.h"
