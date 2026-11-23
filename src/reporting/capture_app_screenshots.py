"""Capture real screenshots of every AeroSense Streamlit page via headless Chrome (CDP)."""
from __future__ import annotations

import base64
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websocket  # websocket-client

from src.config import settings

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE_URL = "http://localhost:8501"
OUT_DIR = settings.REPORTS_DIR / "screens"
DEBUG_PORT = 9333

# (file stem, url path, window height, optional tab labels to click for extra shots)
PAGES = [
    ("scr01_home", "", 1500, []),
    ("scr02_data_explorer", "Global_Data_Explorer", 1700, []),
    ("scr03_analytics", "Pollution_Analytics", 1600, []),
    ("scr04_aqi_intelligence", "AQI_Intelligence", 1700, []),
    ("scr05_forecasting_studio", "Forecasting_Studio", 1900, []),
    ("scr06_model_benchmarking", "Model_Benchmarking", 1700, []),
    ("scr07_explainable_ai", "Explainable_AI", 1700, []),
    ("scr08_spatial_hotspots", "Spatial_Hotspot_Analysis", 2100, []),
    ("scr09_health_advisory", "Health_Risk_and_Advisory", 1800, []),
    ("scr10_research_reports", "Research_Reports", 1700, []),
    ("scr11_system_diagnostics", "System_Diagnostics", 1900, []),
]


class _CDP:
    def __init__(self, ws_url: str) -> None:
        self.ws = websocket.create_connection(ws_url, max_size=None, timeout=60)
        self._id = 0

    def call(self, method: str, **params):
        self._id += 1
        self.ws.send(json.dumps({"id": self._id, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self._id:
                return msg.get("result", {})

    def close(self) -> None:
        self.ws.close()


def _wait_for_chrome() -> str:
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{DEBUG_PORT}/json", timeout=2) as r:
                tabs = json.loads(r.read().decode())
            for t in tabs:
                if t.get("type") == "page":
                    return t["webSocketDebuggerUrl"]
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError("Chrome DevTools endpoint did not come up")


def capture_all(settle_seconds: float = 18.0) -> list[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen([
        CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        f"--remote-debugging-port={DEBUG_PORT}", "--user-data-dir=" + str(OUT_DIR / "_chrome_profile"),
        "--window-size=1500,1200", "about:blank",
    ])
    saved: list[Path] = []
    try:
        cdp = _CDP(_wait_for_chrome())
        cdp.call("Page.enable")
        for stem, path, height, _ in PAGES:
            cdp.call("Emulation.setDeviceMetricsOverride", width=1500, height=height, deviceScaleFactor=1, mobile=False)
            cdp.call("Page.navigate", url=f"{BASE_URL}/{path}")
            time.sleep(settle_seconds)
            shot = cdp.call("Page.captureScreenshot", format="png")
            out = OUT_DIR / f"{stem}.png"
            out.write_bytes(base64.b64decode(shot["data"]))
            saved.append(out)
            print("saved", out.name, out.stat().st_size)
        cdp.close()
    finally:
        proc.terminate()
    return saved


if __name__ == "__main__":
    sys.exit(0 if capture_all() else 1)
