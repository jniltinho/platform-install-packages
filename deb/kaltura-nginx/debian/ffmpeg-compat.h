/* Forced-included (-include) into every nginx object so nginx-vod-module
 * builds against newer FFmpeg without patching its sources.
 * FFmpeg 8 (libavcodec 62) removed avcodec_close(); the module frees the
 * context with av_free() right after, so avcodec_free_context() (which
 * also NULLs the pointer) is a safe replacement. Only version.h is included
 * here: pulling system headers before nginx defines _GNU_SOURCE breaks
 * CPU_SET; the module's own sources include avcodec.h. */
#if defined(__has_include)
#if __has_include(<libavcodec/version.h>)
#include <libavcodec/version.h>
#if LIBAVCODEC_VERSION_MAJOR >= 62
#define avcodec_close(ctx) avcodec_free_context(&(ctx))
#endif
#endif
#endif
