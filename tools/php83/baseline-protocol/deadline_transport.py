"""Whole-operation deadline for the unchanged fixed-origin GET client.

Credentials/URLs are passed only through private process memory, never argv/logs.
The request deadline excludes a bounded terminate/kill/reap cleanup allowance.
"""
import math
import multiprocessing
import time
from guarded_http import BoundaryError, Client, Origin

MAX_BODY = 64 * 1024 * 1024
CLEANUP_GRACE = 0.25

def _worker(origin_fields, ca_pem, ca_pin, url, limit, timeout, buffer, state):
    try:
        origin = Origin(*origin_fields)
        data = Client(origin, ca_pem, ca_pin).get(url, limit=limit, timeout=timeout)
        if not isinstance(data, bytes) or len(data) > limit:
            raise BoundaryError('Invalid response')
        memoryview(buffer).cast('B')[:len(data)] = data
        state.value = len(data)
    except Exception:
        # Never copy an exception, URL, certificate or credential into public IPC.
        state.value = -2

def _bounded(worker, args, *, limit, deadline):
    """Private executor seam for isolated fixture workers, not a URL bypass API."""
    if type(limit) is not int or not 0 < limit <= MAX_BODY:
        raise BoundaryError('Invalid body limit')
    if type(deadline) not in {int, float} or not math.isfinite(deadline) or not 0 < deadline <= 30:
        raise BoundaryError('Invalid total deadline')
    started = time.monotonic()
    ctx = multiprocessing.get_context('spawn')
    buffer = ctx.RawArray('B', limit)
    state = ctx.RawValue('q', -1)
    process = ctx.Process(target=worker, args=(*args, buffer, state), daemon=True)
    launched = False
    try:
        if time.monotonic() - started >= deadline:
            raise BoundaryError('Total deadline exceeded')
        process.start()
        launched = True
        process.join(max(0, deadline - (time.monotonic() - started)))
        if process.is_alive() or time.monotonic() - started >= deadline:
            raise BoundaryError('Total deadline exceeded')
        if process.exitcode != 0 or not 0 <= state.value <= limit:
            raise BoundaryError('Transport request failed')
        data = bytes(memoryview(buffer).cast('B')[:state.value])
        if time.monotonic() - started >= deadline:
            raise BoundaryError('Total deadline exceeded')
        return data
    finally:
        if launched:
            if process.is_alive():
                process.terminate()
                process.join(CLEANUP_GRACE)
            if process.is_alive():
                process.kill()
                process.join(CLEANUP_GRACE)
            if process.is_alive():
                # Fail closed; never report request success with a live worker.
                raise BoundaryError('Transport worker cleanup failed')
            process.join(0)
        process.close()

def get(origin, url, *, ca_pem=None, ca_sha256=None, limit=1024 * 1024,
        deadline=30, socket_timeout=30):
    # Reject subclasses/duck-typed test origins at the production entry point.
    if type(origin) is not Origin:
        raise BoundaryError('Explicit fixed lab origin required')
    origin.validate(url)
    if type(socket_timeout) not in {int, float} or not math.isfinite(socket_timeout) or not 0 < socket_timeout <= 30:
        raise BoundaryError('Invalid socket timeout')
    # Parent validation makes CA/configuration rejection synchronous and sanitized.
    Client(origin, ca_pem, ca_sha256)
    return _bounded(_worker, ((origin.ip, origin.scheme, origin.port), ca_pem,
                    ca_sha256, url, limit, socket_timeout),
                    limit=limit, deadline=deadline)
