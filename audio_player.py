from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path


class AudioPlayer:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.process: subprocess.Popen[bytes] | None = None

    def start(self) -> bool:
        if not self.path.exists():
            return False

        command = self._command()
        if command is None:
            return False

        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        self.process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        return True

    def stop(self) -> None:
        if self.process is None or self.process.poll() is not None:
            return

        self.process.terminate()
        try:
            self.process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            self.process.kill()

    def _command(self) -> list[str] | None:
        system = platform.system()
        path = str(self.path.resolve())

        if system == "Darwin" and shutil.which("afplay"):
            return ["afplay", path]

        if system == "Windows":
            shell = shutil.which("powershell") or shutil.which("pwsh")
            if shell:
                escaped_path = path.replace("'", "''")
                script = (
                    "Add-Type -AssemblyName PresentationCore; "
                    f"$path = '{escaped_path}'; "
                    "$player = New-Object System.Windows.Media.MediaPlayer; "
                    "$player.Open((New-Object System.Uri($path))); "
                    "$player.Play(); "
                    "while (-not $player.NaturalDuration.HasTimeSpan) { "
                    "Start-Sleep -Milliseconds 50 "
                    "} "
                    "Start-Sleep -Milliseconds "
                    "([int][Math]::Ceiling($player.NaturalDuration.TimeSpan.TotalMilliseconds))"
                )
                return [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script]

        players = [
            ("ffplay", ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path]),
            ("mpv", ["mpv", "--no-video", "--really-quiet", path]),
            ("mpg123", ["mpg123", "-q", path]),
            ("cvlc", ["cvlc", "--play-and-exit", "--intf", "dummy", path]),
            ("play", ["play", "-q", path]),
        ]
        for executable, command in players:
            if shutil.which(executable):
                return command

        return None
