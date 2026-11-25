"""Locale-aware UI strings: one language at a time (zh | en)."""
from __future__ import annotations

from typing import Any

from PyQt5.QtCore import QObject, pyqtSignal

from epc_gui.i18n.catalog import CATALOGS, ZH


class I18n(QObject):
    locale_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._locale = "zh"

    @property
    def locale(self) -> str:
        return self._locale

    def set_locale(self, locale: str, *, emit: bool = True) -> None:
        loc = "en" if str(locale).lower().startswith("en") else "zh"
        if loc == self._locale:
            return
        self._locale = loc
        if emit:
            self.locale_changed.emit(loc)

    def tr(self, msgid: str, **kwargs: Any) -> str:
        cat = CATALOGS.get(self._locale) or ZH
        s = cat.get(msgid)
        if s is None:
            s = ZH.get(msgid, msgid)
        if kwargs:
            try:
                return s.format(**kwargs)
            except (KeyError, ValueError, IndexError):
                return s
        return s


_i18n: I18n | None = None


def get_i18n() -> I18n:
    global _i18n
    if _i18n is None:
        _i18n = I18n()
    return _i18n


def tr(msgid: str, **kwargs: Any) -> str:
    return get_i18n().tr(msgid, **kwargs)


def set_locale(locale: str, *, emit: bool = True) -> None:
    get_i18n().set_locale(locale, emit=emit)


def get_locale() -> str:
    return get_i18n().locale
