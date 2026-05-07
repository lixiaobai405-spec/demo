"""Backend entry point — port auto-fallback like Jupyter Notebook."""
import socket
import sys

from app.main import create_app


def find_port(start: int = 8000, max_attempts: int = 100) -> int:
    """Return the first available port starting from `start`."""
    for port in range(start, start + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No available port found in range {start}–{start + max_attempts}")


if __name__ == "__main__":
    import uvicorn

    default = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    port = find_port(default)

    if port != default:
        print(f"[Meitai Demo] Port {default} is busy, using port {port} instead.")
    print(f"[Meitai Demo] Backend → http://localhost:{port}")

    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
