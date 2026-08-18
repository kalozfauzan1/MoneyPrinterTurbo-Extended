import os
import shutil
import socket

import toml
from loguru import logger

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
config_file = os.getenv("MPT_CONFIG_FILE", f"{root_dir}/config.toml")


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default

    try:
        return int(value)
    except ValueError:
        logger.warning(f"invalid integer for {name}: {value!r}; using {default}")
        return default


def load_config():
    config_dir = os.path.dirname(config_file)
    if config_dir:
        os.makedirs(config_dir, exist_ok=True)

    # Keep compatibility with the original fix for an accidentally-created
    # config.toml directory.
    if os.path.isdir(config_file):
        shutil.rmtree(config_file)

    if not os.path.isfile(config_file):
        example_file = f"{root_dir}/config.example.toml"
        if os.path.isfile(example_file):
            shutil.copyfile(example_file, config_file)
            logger.info(f"copy config.example.toml to {config_file}")

    logger.info(f"load config from file: {config_file}")

    try:
        _config_ = toml.load(config_file)
    except Exception as e:
        logger.warning(f"load config failed: {str(e)}, try to load as utf-8-sig")
        with open(config_file, mode="r", encoding="utf-8-sig") as fp:
            _cfg_content = fp.read()
            _config_ = toml.loads(_cfg_content)

    return _config_


def save_config():
    config_dir = os.path.dirname(config_file)
    if config_dir:
        os.makedirs(config_dir, exist_ok=True)

    with open(config_file, "w", encoding="utf-8") as f:
        _cfg["app"] = app
        _cfg["azure"] = azure
        _cfg["siliconflow"] = siliconflow
        _cfg["ui"] = ui
        f.write(toml.dumps(_cfg))


_cfg = load_config()

app = _cfg.get("app", {})
whisper = _cfg.get("whisper", {})
proxy = _cfg.get("proxy", {})
azure = _cfg.get("azure", {})
siliconflow = _cfg.get("siliconflow", {})

ui = _cfg.get(
    "ui",
    {
        "hide_log": False,
    },
)

# Runtime overrides for Docker / Dokploy.
# If an env variable is absent, config.toml remains the source of truth.
app["enable_redis"] = _env_bool(
    "MPT_REDIS_ENABLED",
    bool(app.get("enable_redis", False)),
)

app["redis_host"] = os.getenv(
    "MPT_REDIS_HOST",
    app.get("redis_host", "localhost"),
)

app["redis_port"] = _env_int(
    "MPT_REDIS_PORT",
    int(app.get("redis_port", 6379)),
)

app["redis_db"] = _env_int(
    "MPT_REDIS_DB",
    int(app.get("redis_db", 0)),
)

if "MPT_REDIS_PASSWORD" in os.environ:
    app["redis_password"] = os.environ["MPT_REDIS_PASSWORD"]

app["max_concurrent_tasks"] = _env_int(
    "MPT_MAX_CONCURRENT_TASKS",
    int(app.get("max_concurrent_tasks", 5)),
)

hostname = socket.gethostname()

log_level = _cfg.get("log_level", "DEBUG")

listen_host = os.getenv(
    "MPT_LISTEN_HOST",
    _cfg.get("listen_host", "0.0.0.0"),
)

listen_port = _env_int(
    "MPT_LISTEN_PORT",
    int(_cfg.get("listen_port", 8080)),
)

project_name = _cfg.get("project_name", "MoneyPrinterTurbo")

project_description = _cfg.get(
    "project_description",
    "<a href='https://github.com/harry0703/MoneyPrinterTurbo'>https://github.com/harry0703/MoneyPrinterTurbo</a>",
)

project_version = _cfg.get("project_version", "1.2.6")
reload_debug = False

imagemagick_path = app.get("imagemagick_path", "")
if imagemagick_path and os.path.isfile(imagemagick_path):
    os.environ["IMAGEMAGICK_BINARY"] = imagemagick_path

ffmpeg_path = app.get("ffmpeg_path", "")
if ffmpeg_path and os.path.isfile(ffmpeg_path):
    os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_path

logger.info(f"{project_name} v{project_version}")
