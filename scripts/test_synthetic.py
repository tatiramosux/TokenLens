"""Test entrypoint: deny outbound network and provider executable invocation."""
import os
import socket
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
connect = socket.socket.connect
popen = subprocess.Popen

def local_only(sock, address):
    if not isinstance(address, tuple) or address[0] not in ("127.0.0.1", "::1"):
        raise RuntimeError("Rede externa proibida na suite sintetica.")
    return connect(sock, address)

def python_only(args, *a, **kw):
    if not isinstance(args, (list, tuple)) or Path(args[0]).resolve() != Path(sys.executable).resolve():
        raise RuntimeError("Somente subprocessos Python sinteticos sao permitidos.")
    return popen(args, *a, **kw)

if __name__ == "__main__":
    os.chdir(ROOT)
    with patch.object(socket.socket, "connect", local_only), patch.object(subprocess, "Popen", python_only):
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT/"core"/"tests")))
    raise SystemExit(not result.wasSuccessful())
