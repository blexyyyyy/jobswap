try:
    from app.main import app
except Exception as e:
    import traceback
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    error_trace = traceback.format_exc()
    
    @app.get("/{path:path}")
    async def catch_all(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Critical Startup Error", 
                "error": str(e), 
                "trace": error_trace
            }
        )
