import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def install_linux_service():
    home = Path.home()
    service_dir = home / ".config/systemd/user"
    service_dir.mkdir(parents=True, exist_ok=True)

    service_file = service_dir / "rudolph.service"
    python_exec = shutil.which("python") or sys.executable
    rudolph_path = shutil.which("rudolph") or f"{home}/.local/bin/rudolph"

    service_content = f"""[Unit]
Description=Rudolph Launcher Service
After=default.target

[Service]
Type=simple
ExecStart={python_exec} {rudolph_path}
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
"""
    service_file.write_text(service_content)
    print(f"[+] Service file created at {service_file}")

    # Enable and start service
    subprocess.run(["systemctl", "--user", "daemon-reload"])
    subprocess.run(["systemctl", "--user", "enable", "--now", "rudolph.service"])
    print("[+] Rudolph service installed and started!")

def install_windows_startup():
    home = Path.home()
    startup_dir = home / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
    startup_dir.mkdir(parents=True, exist_ok=True)

    rudolph_path = shutil.which("rudolph") or f"{home}\\.local\\bin\\rudolph.exe"
    shortcut_path = startup_dir / "Rudolph.lnk"

    try:
        import pythoncom
        from win32com.shell import shell, shellcon
        import win32com.client

        shell_obj = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell_obj.CreateShortcut(str(shortcut_path))
        shortcut.TargetPath = rudolph_path
        shortcut.WorkingDirectory = str(home)
        shortcut.Save()
        print(f"[+] Shortcut created at {shortcut_path}")
    except ImportError:
        print("[!] pywin32 is required to create the Startup shortcut. Install with `pip install pywin32`.")
        print(f"[!] Or manually create a shortcut to {rudolph_path} in {startup_dir}")

def main():
    current_os = platform.system()
    if current_os == "Linux":
        install_linux_service()
        print("[i] Reminder: set your custom shortcut in GNOME/KDE manually.")
    elif current_os == "Windows":
        install_windows_startup()
        print("[i] Shortcut will work if you use the combination in `settings.ini`.")
    else:
        print(f"[!] OS {current_os} is not supported by this installer.")

if __name__ == "__main__":
    main()