from datetime import datetime
from pathlib import Path


class RunContext:
    """
    Project Polarisの1回の実行単位を管理するクラス。

    例:
    output/2026-07-04/run_180955/
    """

    def __init__(self, base_dir: str = "output"):
        now = datetime.now()

        self.created_at = now
        self.date_text = now.date().isoformat()
        self.run_id = f"run_{now.strftime('%H%M%S')}"

        self.base_dir = Path(base_dir)
        self.run_dir = self._create_run_dir()

    def _create_run_dir(self) -> Path:
        """
        実行用ディレクトリを作成する。
        同じ秒に実行された場合は連番を付ける。
        """

        date_dir = self.base_dir / self.date_text
        date_dir.mkdir(parents=True, exist_ok=True)

        run_dir = date_dir / self.run_id

        counter = 1
        while run_dir.exists():
            run_dir = date_dir / f"{self.run_id}_{counter:02d}"
            counter += 1

        run_dir.mkdir(parents=True, exist_ok=True)

        return run_dir
