import time

from fastapi import Request


async def request_logging_middleware(
    request: Request,
    call_next
):

    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    print(
        f"{request.method} "
        f"{request.url.path} "
        f"-> {response.status_code} "
        f"({process_time:.4f}s)"
    )

    response.headers["X-Process-Time"] = str(
        round(process_time, 4)
    )

    return response
