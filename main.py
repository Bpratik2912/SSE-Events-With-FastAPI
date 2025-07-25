import uvicorn, asyncio, logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from fastapi.responses import StreamingResponse

# register the App
app = FastAPI()

# register middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register logging
logging.basicConfig(
    level=logging.DEBUG,  # or logging.INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("timer.log")
    ]
)

# define the get logger
logger = logging.getLogger(__name__)

# function to get current date and time
def get_current_time():
    return f"Current date and time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"


# define an asynchronous generator that yields data periodically — it’s the core of SSE.
async def event_generator(request: Request):
    client = request.client
    logger.debug(f"request initiated by {client}")
    try:
        while True:
            if await request.is_disconnected():
                logger.debug(f"request ended by {client}")
                break

            yield get_current_time()
            await asyncio.sleep(1)
    except asyncio.CancelledError:

        # This catches disconnects not caught by `is_disconnected`
        logger.debug(f"request forcibly cancelled by {client}")
        raise
    finally:

        # Always logs on exit (graceful or not)
        logger.debug(f"streaming ended for {client}")


@app.get("/current_time")
async def current_time(request: Request):
    return StreamingResponse(
        event_generator(request),
        media_type="text/event-stream"
    )

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

