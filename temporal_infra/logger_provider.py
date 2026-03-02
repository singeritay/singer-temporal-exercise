import logging
import sys
from collections.abc import Mapping
from typing import Any, Optional


class TemporalLogger:
    def __init__(
            self,
            name: str = "temporal_infra",
            level: int = logging.INFO,
            extra: Optional[dict[str, Any]] = None,
            log_format: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s%(extra_text)s",
            date_format: str = "%Y-%m-%d %H:%M:%S",
    ):
        self._extra = dict(extra or {})
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(level)
            handler.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format, defaults={'extra_text': ''}))
            self.logger.addHandler(handler)

    def _merge_extra(self, extra: Optional[Mapping[str, Any]]) -> dict[str, Any]:
        if not extra:
            return dict(self._extra)
        merged = dict(self._extra)
        merged.update(dict(extra))
        return merged

    def _build_extra_payload(self, extra: Optional[Mapping[str, Any]]) -> dict[str, Any]:
        merged_extra = self._merge_extra(extra)
        if not merged_extra:
            return {"extra_text": ""}
        return {"extra_text": f" | {merged_extra}"}

    def debug(self, message: str, *args: Any, extra: Optional[dict[str, Any]] = None, **kwargs: Any) -> None:
        self.logger.debug(message, *args, extra=self._build_extra_payload(extra), **kwargs)

    def info(self, message: str, *args: Any, extra: Optional[dict[str, Any]] = None, **kwargs: Any) -> None:
        self.logger.info(message, *args, extra=self._build_extra_payload(extra), **kwargs)

    def warning(self, message: str, *args: Any, extra: Optional[dict[str, Any]] = None, **kwargs: Any) -> None:
        self.logger.warning(message, *args, extra=self._build_extra_payload(extra), **kwargs)

    def error(self, message: str, *args: Any, extra: Optional[dict[str, Any]] = None, **kwargs: Any) -> None:
        self.logger.error(message, *args, extra=self._build_extra_payload(extra), **kwargs)

    def exception(self, message: str, *args: Any, extra: Optional[dict[str, Any]] = None, **kwargs: Any) -> None:
        self.logger.exception(message, *args, extra=self._build_extra_payload(extra), **kwargs)

    def critical(self, message: str, *args: Any, extra: Optional[dict[str, Any]] = None, **kwargs: Any) -> None:
        self.logger.critical(message, *args, extra=self._build_extra_payload(extra), **kwargs)
