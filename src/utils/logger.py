import logging
from datetime import date
from pathlib import Path


def setup_logger(
    name: str = "polaris",
    base_dir: str = "logs",
) -> logging.Logger:
    """
    Project Polaris用のロガーを作成する。

    logs/YYYY-MM-DD.log に実行ログを保存する。
    """

    log_dir = Path(base_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_path = log_dir / f"{date.today().isoformat()}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # すでにHandlerが設定されている場合は重複追加しない
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(
        log_path,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
