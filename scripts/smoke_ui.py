"""Run using the installed package's Python, without frontend or browser dependencies."""

from __future__ import annotations

import http.client
import json
import sys
import threading
from pathlib import Path

from fail2test.ui.server import LocalServer, Workspace


def main() -> None:
    workspace = Workspace(Path(sys.argv[1]))
    server = LocalServer(workspace, 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        for path, expected in [
            ("/", b"Fail2Test"),
            ("/assets/app.js", b"startJob"),
            ("/assets/app.css", b"--green"),
        ]:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port)
            connection.request("GET", path)
            response = connection.getresponse()
            assert response.status == 200
            assert expected in response.read()
            connection.close()
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port)
        connection.request(
            "GET",
            "/api/workspace",
            headers={
                "Authorization": f"Bearer {server.token}",
                "Origin": server.origin,
            },
        )
        response = connection.getresponse()
        assert response.status == 200
        assert set(json.loads(response.read())["runners"]) == {"broken", "fixed"}
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print("Installed UI assets and authenticated loopback API verified.")


if __name__ == "__main__":
    main()
