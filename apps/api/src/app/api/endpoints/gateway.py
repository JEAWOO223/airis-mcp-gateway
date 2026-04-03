"""Gateway control endpoints"""
import asyncio
import os

from fastapi import APIRouter, HTTPException, status

router = APIRouter(tags=["gateway"])


def _project_root() -> str:
    return os.getenv(
        "PROJECT_ROOT",
        os.getenv("CONTAINER_PROJECT_ROOT", "/workspace/project"),
    )


async def _run_compose(*args: str, timeout: int = 30) -> asyncio.subprocess.Process:
    proc = await asyncio.create_subprocess_exec(
        "docker", "compose", *args,
        cwd=_project_root(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise
    return proc


@router.post("/restart", response_model=dict)
async def restart_gateway():
    """Restart MCP Gateway to apply new secrets"""
    try:
        proc = await _run_compose("restart", "mcp-gateway", timeout=30)

        if proc.returncode != 0:
            stderr = (await proc.stderr.read()).decode() if proc.stderr else ""
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to restart gateway: {stderr}",
            )

        stdout = (await proc.stdout.read()).decode() if proc.stdout else ""
        return {
            "status": "success",
            "message": "MCP Gateway restarted successfully",
            "output": stdout,
        }

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Gateway restart timeout",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.get("/status", response_model=dict)
async def gateway_status():
    """Get MCP Gateway status"""
    try:
        proc = await _run_compose("ps", "mcp-gateway", timeout=10)
        stdout = (await proc.stdout.read()).decode() if proc.stdout else ""
        is_running = "Up" in stdout

        return {
            "status": "running" if is_running else "stopped",
            "details": stdout,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get gateway status: {str(e)}",
        )
