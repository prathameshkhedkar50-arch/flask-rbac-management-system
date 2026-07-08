import argparse
import atexit
import os
import platform
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT=Path(__file__).resolve().parent
FRONTEND_DIR=ROOT/"frontend"/"dashboard"
BACKEND_RUN=ROOT/"backend"/"run.py"
VENV_DIR=ROOT/"venv"
STATE_DIR=ROOT/".setup_state"
BACKEND_MARKER=STATE_DIR/"backend.ok"
FRONTEND_MARKER=STATE_DIR/"frontend.ok"
DB_NAME="rbac_db"
DB_USER="postgres"
DB_HOST="localhost"

processes=[]
start_time=time.time()
shutting_down=False

class Log:
    COLORS={
        "INFO":"\033[94m",
        "SUCCESS":"\033[92m",
        "WARNING":"\033[93m",
        "ERROR":"\033[91m",
        "RUN":"\033[96m",
        "END":"\033[0m"
    }

    @staticmethod
    def _supports_color():
        return sys.stdout.isatty()

    @classmethod
    def write(cls,level,msg):
        if cls._supports_color():
            color=cls.COLORS.get(level,"")
            end=cls.COLORS["END"]
            print(f"{color}[{level}]{end} {msg}")
        else:
            print(f"[{level}] {msg}")

    @classmethod
    def info(cls,msg):
        cls.write("INFO",msg)

    @classmethod
    def success(cls,msg):
        cls.write("SUCCESS",msg)

    @classmethod
    def warning(cls,msg):
        cls.write("WARNING",msg)

    @classmethod
    def error(cls,msg):
        cls.write("ERROR",msg)

    @classmethod
    def run(cls,msg):
        cls.write("RUN",msg)

def load_env_file(path):
    if not path.exists():
        return

    Log.info(f"Loading environment from {path.name}")

    for raw_line in path.read_text(encoding="utf-8",errors="ignore").splitlines():
        line=raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key,value=line.split("=",1)
        key=key.strip()
        value=value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key]=value

def load_env():
    load_env_file(ROOT/".env")
    load_env_file(ROOT/".env.local")

def config_db_password():
    config_path=ROOT/"backend"/"app"/"config.py"

    if not config_path.exists():
        return None

    text=config_path.read_text(encoding="utf-8",errors="ignore")

    for line in text.splitlines():
        if "SQLALCHEMY_DATABASE_URI" not in line or "=" not in line:
            continue

        value=line.split("=",1)[1].strip().strip('"').strip("'")

        try:
            parsed=urlparse(value)
            if parsed.password:
                return unquote(parsed.password)
        except ValueError:
            return None

    return None

def postgres_password():
    password=os.environ.get("PGPASSWORD")

    if password:
        Log.info("Using PostgreSQL password from environment variable")
        return password

    for key in ("POSTGRES_PASSWORD","DB_PASSWORD","DATABASE_PASSWORD"):
        password=os.environ.get(key)
        if password:
            Log.info(f"Using PostgreSQL password from {key}")
            return password

    password=config_db_password()

    if password:
        Log.info("Using PostgreSQL password from backend/app/config.py")
        os.environ["PGPASSWORD"]=password
        return password

    if sys.stdin.isatty():
        Log.warning("PGPASSWORD is missing; asking once for PostgreSQL password")
        password=input("PostgreSQL password: ")
        os.environ["PGPASSWORD"]=password
        return password

    fail(
        "PostgreSQL password not found.",
        [
            "Set PGPASSWORD in .env, .env.local, or your shell.",
            "Example: PGPASSWORD=pgadmin",
            "The setup is non-interactive, so it cannot prompt for a password."
        ]
    )

def is_windows():
    return platform.system().lower()=="windows"

def command_name(name):
    found=shutil.which(name)

    if found:
        return found

    if is_windows() and not name.endswith(".cmd"):
        return shutil.which(f"{name}.cmd")

    return None

def venv_python():
    return VENV_DIR/"Scripts"/"python.exe" if is_windows() else VENV_DIR/"bin"/"python"

def venv_pip():
    return VENV_DIR/"Scripts"/"pip.exe" if is_windows() else VENV_DIR/"bin"/"pip"

def node_modules_healthy():
    return (FRONTEND_DIR/"node_modules").exists() and FRONTEND_MARKER.exists()

def venv_healthy():
    return venv_python().exists() and venv_pip().exists()

def backend_deps_healthy():
    return venv_healthy() and BACKEND_MARKER.exists()

def mark(path):
    STATE_DIR.mkdir(exist_ok=True)
    path.write_text(str(time.time()),encoding="utf-8")

def fail(message,fixes=None,code=1):
    Log.error(message)

    if fixes:
        for fix in fixes:
            print(f"  - {fix}")

    sys.exit(code)

def run_cmd(cmd,step,cwd=ROOT,env=None,retries=1):
    env=env or os.environ.copy()

    for attempt in range(1,retries+1):
        display=" ".join(str(part) for part in cmd)
        suffix=f" (attempt {attempt}/{retries})" if retries>1 else ""
        Log.run(f"{step}: {display}{suffix}")

        try:
            subprocess.check_call([str(part) for part in cmd],cwd=str(cwd),env=env)
            return
        except FileNotFoundError:
            fail(
                f"Missing command while running {step}: {cmd[0]}",
                dependency_fix(str(cmd[0]))
            )
        except subprocess.CalledProcessError as exc:
            if attempt<retries:
                Log.warning(f"{step} failed; retrying shortly")
                time.sleep(2)
                continue

            fail_step(step,cmd,exc.returncode)

def command_output(cmd,cwd=ROOT):
    return subprocess.check_output(
        [str(part) for part in cmd],
        cwd=str(cwd),
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore"
    ).strip()

def fail_step(step,cmd,return_code):
    display=" ".join(str(part) for part in cmd)
    Log.error(f"Step failed: {step}")
    print(f"[FAILED CMD] {display}")
    print(f"[EXIT CODE] {return_code}")

    fixes={
        "VENV":[
            "Close terminals/editors using the venv folder and retry.",
            "Run: python setup.py clean --force",
            "Repair or reinstall Python if venvlauncher.exe copy errors continue."
        ],
        "BACKEND INSTALL":[
            "Check internet access and pip availability.",
            "Try: python -m pip install --upgrade pip",
            "If psycopg2 fails, confirm Python and PostgreSQL client compatibility."
        ],
        "FRONTEND INSTALL":[
            "Confirm Node.js and npm are installed.",
            "Delete frontend/dashboard/node_modules and retry.",
            "Check npm registry/network access."
        ],
        "FRONTEND BUILD":[
            "Open the TypeScript error above and fix the reported file/line.",
            "Then rerun: python setup.py fresh --no-start"
        ],
        "DB":[
            "Confirm PostgreSQL service is running.",
            "Confirm psql is installed and available on PATH.",
            "Confirm PGPASSWORD is correct."
        ],
        "BACKEND START":[
            "Confirm venv dependencies are installed.",
            "Confirm PostgreSQL is running and rbac_db exists."
        ],
        "FRONTEND START":[
            "Confirm node_modules exists.",
            "Run: python setup.py fresh --no-start"
        ]
    }

    for key,items in fixes.items():
        if key in step:
            for item in items:
                print(f"  - {item}")
            break
    else:
        print("  - Review the failed command output above and rerun setup.")

    sys.exit(return_code or 1)

def dependency_fix(command):
    name=Path(command).name.lower()

    if "node" in name or "npm" in name:
        return [
            "Install Node.js LTS and ensure node/npm are on PATH.",
            "Close and reopen Git Bash/PowerShell after installing Node.js."
        ]

    if "psql" in name:
        return [
            "Install PostgreSQL client tools.",
            "Add PostgreSQL bin folder to PATH, for example C:\\Program Files\\PostgreSQL\\17\\bin."
        ]

    if "python" in name:
        return [
            "Install Python 3.11+ and enable Add Python to PATH.",
            "Use the Python launcher or run this setup with the desired Python executable."
        ]

    return ["Install the missing command and ensure it is on PATH."]

def validate_dependencies(include_frontend=True,include_db=True):
    Log.info("Validating required developer tools")

    if not Path(sys.executable).exists():
        fail("Python executable was not found.",dependency_fix("python"))

    Log.success(f"Python found: {sys.executable}")

    try:
        subprocess.check_call(
            [sys.executable,"-m","pip","--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        Log.success("pip found through current Python")
    except (subprocess.CalledProcessError,FileNotFoundError):
        fail(
            "pip was not found for the current Python.",
            [
                "Repair Python and ensure pip is installed.",
                "Try: python -m ensurepip --upgrade",
                "Then rerun setup."
            ]
        )

    if include_frontend:
        for name in ("node","npm"):
            found=command_name(name)
            if not found:
                fail(f"{name} was not found on PATH.",dependency_fix(name))
            version_arg="--version"
            try:
                version=command_output([found,version_arg])
                Log.success(f"{name} found: {found} ({version})")
            except (subprocess.CalledProcessError,FileNotFoundError):
                Log.success(f"{name} found: {found}")

    if include_db:
        found=command_name("psql")
        if not found:
            fail("psql was not found on PATH.",dependency_fix("psql"))
        try:
            version=command_output([found,"--version"])
            Log.success(f"psql found: {found} ({version})")
        except (subprocess.CalledProcessError,FileNotFoundError):
            Log.success(f"psql found: {found}")

def remove_path(path):
    path=Path(path)

    if not path.exists():
        return False

    for attempt in range(1,4):
        try:
            if is_windows() and path.is_dir():
                for child in path.rglob("*"):
                    try:
                        child.chmod(0o700)
                    except OSError:
                        pass
            if path.is_dir():
                shutil.rmtree(path,ignore_errors=False)
            else:
                path.unlink(missing_ok=True)
            Log.success(f"Removed {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
            return True
        except PermissionError:
            Log.warning(f"Permission denied removing {path}; retrying after closing possible file handles")
            time.sleep(1.5)
        except OSError as exc:
            Log.warning(f"Could not remove {path}: {exc}")
            time.sleep(1)

    if path.exists():
        Log.warning(f"Skipped locked path: {path}")
        return False

    return True

def clean(force=False,include_venv=True,include_node=True):
    Log.info("Cleaning generated project files")
    removed=0

    direct_paths=[
        ROOT/"frontend"/"dashboard"/"dist",
        ROOT/".idea",
        ROOT/".pytest_cache",
        ROOT/".mypy_cache",
        ROOT/".ruff_cache",
        ROOT/"build",
        ROOT/"dist"
    ]

    if include_venv:
        direct_paths.insert(0,VENV_DIR)

    if include_node:
        direct_paths.append(FRONTEND_DIR/"node_modules")

    if force:
        direct_paths.append(STATE_DIR)

    for path in direct_paths:
        if remove_path(path):
            removed+=1

    patterns=[
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.tmp",
        "*.temp",
        "*.log",
        "*.pid",
        "*.lock.tmp",
        "npm-debug.log",
        "yarn-error.log",
        ".vite",
        ".cache"
    ]

    protected_parts={"backend","frontend","src","app"}

    for pattern in patterns:
        for path in ROOT.rglob(pattern):
            if not path.exists():
                continue

            if path.name in protected_parts:
                continue

            if "node_modules" in path.parts and path.name!="node_modules":
                continue

            if remove_path(path):
                removed+=1

    Log.success(f"Cleanup completed; removed {removed} generated paths")

    if force:
        Log.info("Force cleanup requested; generated dependency folders were included")

def recreate_venv(force=False):
    if venv_healthy() and not force:
        Log.success("Virtual environment already exists and looks healthy")
        return

    if VENV_DIR.exists():
        Log.info("Removing old virtual environment")
        if not remove_path(VENV_DIR):
            fail(
                "Unable to remove existing virtual environment.",
                [
                    "Close terminals/editors using files inside venv.",
                    "Stop Python processes that may be running from this project.",
                    "Then rerun: python setup.py fresh --force"
                ]
            )

    Log.info("Creating fresh virtual environment")
    time.sleep(1)

    venv_commands=[
        [sys.executable,"-m","venv",str(VENV_DIR)],
    ]

    if is_windows():
        venv_commands.append([sys.executable,"-m","venv","--copies",str(VENV_DIR)])

    for attempt in range(1,4):
        try:
            cmd=venv_commands[min(attempt-1,len(venv_commands)-1)]
            Log.run(f"VENV: {' '.join(str(part) for part in cmd)} (attempt {attempt}/3)")
            subprocess.check_call(cmd,cwd=str(ROOT))

            if venv_healthy():
                Log.success("Virtual environment created successfully")
                return
        except subprocess.CalledProcessError as exc:
            if is_windows() and "venvlauncher" in str(exc).lower():
                Log.warning("Virtual environment creation hit the Windows launcher copy issue")
            else:
                Log.warning("Virtual environment creation failed")
        except OSError as exc:
            Log.warning(f"Virtual environment creation failed: {exc}")

        Log.warning("Virtual environment creation did not complete; cleaning partial venv before retry")
        remove_path(VENV_DIR)
        time.sleep(2)

    fail(
        "Virtual environment creation failed after retries.",
        [
            "Close file explorers, terminals, and editors that may lock venv files.",
            "Repair Python installation if venvlauncher.exe copy errors continue.",
            "Try from PowerShell if Git Bash keeps a file handle open."
        ]
    )

def install_backend(force=False):
    recreate_venv(force=force)

    if backend_deps_healthy() and not force:
        Log.success("Backend dependencies already installed")
        return

    if not venv_pip().exists():
        fail("pip is missing inside the virtual environment.",["Recreate venv: python setup.py fresh --force"])

    Log.info("Installing backend dependencies")
    run_cmd([venv_python(),"-m","pip","install","--upgrade","pip"],"BACKEND INSTALL",retries=2)
    run_cmd(
        [venv_python(),"-m","pip","install","flask","flask_sqlalchemy","psycopg2-binary","flask_cors"],
        "BACKEND INSTALL",
        retries=2
    )
    mark(BACKEND_MARKER)
    Log.success("Backend dependencies installed")

def install_frontend(force=False):
    if node_modules_healthy() and not force:
        Log.success("Frontend dependencies already installed")
        return

    Log.info("Installing frontend dependencies")
    npm=command_name("npm")

    if not npm:
        fail("npm was not found on PATH.",dependency_fix("npm"))

    run_cmd([npm,"install"],"FRONTEND INSTALL",cwd=FRONTEND_DIR,retries=2)
    mark(FRONTEND_MARKER)
    Log.success("Frontend dependencies installed")

def build_frontend():
    Log.info("Building frontend")
    npm=command_name("npm")

    if not npm:
        fail("npm was not found on PATH.",dependency_fix("npm"))

    run_cmd([npm,"run","build"],"FRONTEND BUILD",cwd=FRONTEND_DIR,retries=1)
    Log.success("Frontend build completed")

def db_env(password):
    env=os.environ.copy()
    env["PGPASSWORD"]=password
    return env

def db_reset(password):
    Log.info("Resetting PostgreSQL database")
    psql=command_name("psql")

    if not psql:
        fail("psql was not found on PATH.",dependency_fix("psql"))

    env=db_env(password)

    commands=[
        ["-U",DB_USER,"-h",DB_HOST,"-d","postgres","-c",f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{DB_NAME}' AND pid <> pg_backend_pid();"],
        ["-U",DB_USER,"-h",DB_HOST,"-d","postgres","-c",f"DROP DATABASE IF EXISTS {DB_NAME};"],
        ["-U",DB_USER,"-h",DB_HOST,"-d","postgres","-c",f"CREATE DATABASE {DB_NAME};"]
    ]

    for args in commands:
        run_cmd([psql,*args],"DB RESET",env=env,retries=1)

    Log.success("Database reset completed")

def validate_project():
    Log.info("Validating project structure")

    required=[
        ROOT/"backend"/"app",
        ROOT/"backend"/"app"/"routes.py",
        ROOT/"backend"/"app"/"models.py",
        BACKEND_RUN,
        FRONTEND_DIR,
        FRONTEND_DIR/"package.json",
        FRONTEND_DIR/"src"
    ]

    missing=[str(path.relative_to(ROOT)) for path in required if not path.exists()]

    if missing:
        fail(
            "Project structure is incomplete.",
            [f"Missing: {item}" for item in missing]+["Restore the missing files before running setup."]
        )

    Log.success("Project structure looks valid")

def port_in_use(port):
    import socket

    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1",port))==0

def validate_run_ready():
    validate_project()

    if not venv_healthy():
        fail(
            "Virtual environment is missing or corrupted.",
            ["Run: python setup.py fresh --no-start"]
        )

    if not (FRONTEND_DIR/"node_modules").exists():
        fail(
            "Frontend dependencies are missing.",
            ["Run: python setup.py fresh --no-start"]
        )

    for port,label in ((5000,"Flask backend"),(5173,"Vite frontend")):
        if port_in_use(port):
            Log.warning(f"Port {port} is already in use; {label} may choose another port or fail")

def terminate_process(process,label):
    if not process or process.poll() is not None:
        return

    Log.info(f"Stopping {label}")

    try:
        if is_windows():
            subprocess.call(["taskkill","/T","/PID",str(process.pid)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            time.sleep(1)
            if process.poll() is None:
                subprocess.call(["taskkill","/F","/T","/PID",str(process.pid)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        else:
            process.terminate()
            process.wait(timeout=5)
    except Exception as exc:
        Log.warning(f"Could not stop {label} cleanly: {exc}")

def cleanup_processes():
    global shutting_down
    if shutting_down:
        return
    shutting_down=True
    for process,label in reversed(processes):
        terminate_process(process,label)

def start():
    validate_dependencies(include_frontend=True,include_db=False)
    validate_run_ready()

    Log.info("Starting backend + frontend")
    npm=command_name("npm")

    if not npm:
        fail("npm was not found on PATH.",dependency_fix("npm"))

    backend=subprocess.Popen([str(venv_python()),str(BACKEND_RUN)],cwd=str(ROOT))
    processes.append((backend,"backend"))

    time.sleep(2)

    frontend=subprocess.Popen([npm,"run","dev"],cwd=str(FRONTEND_DIR))
    processes.append((frontend,"frontend"))

    Log.success("Backend and frontend processes started")
    Log.info("Press Ctrl+C to stop both processes")

    try:
        while True:
            if backend.poll() is not None:
                cleanup_processes()
                fail("Backend process exited unexpectedly.",["Check backend logs above and PostgreSQL status."])

            if frontend.poll() is not None:
                cleanup_processes()
                fail("Frontend process exited unexpectedly.",["Check frontend logs above and npm dependencies."])

            time.sleep(1)
    except KeyboardInterrupt:
        Log.info("Stopped by user (Ctrl+C)")
    finally:
        cleanup_processes()
        clean(include_venv=False,include_node=False)
        Log.success("Runtime cleanup completed")

def fresh(args):
    force=args.force
    validate_project()
    validate_dependencies(include_frontend=True,include_db=True)
    password=postgres_password()

    clean(force=force,include_venv=force,include_node=force)
    install_backend(force=force)
    db_reset(password)
    install_frontend(force=force)
    build_frontend()

    if args.no_start:
        Log.success("Fresh setup completed without starting servers")
        return

    start()

def parse_args():
    parser=argparse.ArgumentParser(description="RBAC project setup utility")
    sub=parser.add_subparsers(dest="command")

    fresh_parser=sub.add_parser("fresh",help="Prepare dependencies, reset DB, build frontend, and optionally run")
    fresh_parser.add_argument("--force",action="store_true",help="Recreate venv and node_modules even if healthy")
    fresh_parser.add_argument("--no-start",action="store_true",help="Complete setup without starting backend/frontend")

    run_parser=sub.add_parser("run",help="Run backend and frontend")
    run_parser.set_defaults(command="run")

    clean_parser=sub.add_parser("clean",help="Remove generated files")
    clean_parser.add_argument("--force",action="store_true",help="Also remove dependency folders")

    return parser.parse_args()

def main():
    load_env()
    atexit.register(cleanup_processes)
    args=parse_args()

    if not args.command:
        print("Use: python setup.py fresh [--force] [--no-start] OR python setup.py run OR python setup.py clean [--force]")
        sys.exit(1)

    try:
        if args.command=="fresh":
            fresh(args)
        elif args.command=="run":
            start()
        elif args.command=="clean":
            clean(force=args.force,include_venv=args.force,include_node=args.force)
        else:
            fail(f"Unknown command: {args.command}")
    finally:
        elapsed=time.time()-start_time
        Log.info(f"Setup utility finished in {elapsed:.1f}s")

if __name__=="__main__":
    def handle_stop(*_):
        Log.info("Stop signal received; cleaning up child processes")
        cleanup_processes()
        sys.exit(0)

    if hasattr(signal,"SIGTERM"):
        signal.signal(signal.SIGTERM,handle_stop)
    if hasattr(signal,"SIGINT"):
        signal.signal(signal.SIGINT,handle_stop)

    main()
