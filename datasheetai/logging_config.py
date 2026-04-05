import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

# moved to config file
# class LoggingConfig:
#     level: str = "DEBUG"
#     log_dir: str = "logs"
#     log_file: str = f"datasheetai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
#     max_bytes: int = 5_242_880  # 5 MB
#     backup_count: int = 3
#     format: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
#     date_format: str = "%Y-%m-%d %H:%M:%S"
from datasheetai.config import LoggingConfig

def setup_logging(config: LoggingConfig) -> None:
    """
    Configure root logger once at application startup.

    All child loggers from module-level `logging.getLogger(__name__)` inherit this root configuration automatically
    """
    log_dir = Path(config.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{config.log_file}_{timestamp}.log"

    formatter = logging.Formatter(
        fmt=config.format,
        datefmt=config.date_format,
    )

    # Console handler with same formatter for nice CLI output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Rotating file handler to prevent log files from growing indefinitely
    file_handler = logging.handlers.RotatingFileHandler(
        filename = log_dir / log_filename,
        maxBytes = config.max_bytes,
        backupCount = config.backup_count,
        encoding = "utf-8",
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()  # the root logger that all module loggers inherit from
    root_logger.setLevel(config.level.upper())
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)