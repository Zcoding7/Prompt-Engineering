import flet as ft
import threading
import subprocess
import time
import urllib.request

def start_streamlit():
    subprocess.Popen(
        ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def wait_for_server(url="http://localhost:8501", timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(url)
            return True
        except Exception:
            time.sleep(0.5)
    return False

def main(page: ft.Page):
    page.title = "Prompt Engineering Studio"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK

    loading = ft.Container(
        content=ft.Column(
            [
                ft.ProgressRing(),
                ft.Text("Starting Prompt Engineering Studio...", size=16)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        expand=True,
        alignment=ft.alignment.center
    )
    page.add(loading)

    threading.Thread(target=start_streamlit, daemon=True).start()

    if wait_for_server():
        page.controls.clear()
        page.add(
            ft.WebView(
                url="http://localhost:8501",
                expand=True,
                javascript_enabled=True
            )
        )
        page.update()

ft.app(target=main)
