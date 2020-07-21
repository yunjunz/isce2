#ifndef __DEBUG_H
#define __DEBUG_H

#include <iostream>
#include <assert.h>
#include <stdio.h>

#ifndef NDEBUG
#define CUAMPCOR_DEBUG
#define CUDA_ERROR_CHECK
#define debugmsg(msg) fprintf(stderr, msg)
#else
#define debugmsg(msg)
#endif //NDEBUG

#endif //__DEBUG_H
