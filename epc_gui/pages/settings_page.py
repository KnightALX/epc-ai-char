"""Page D — app settings: dark-mode switch + language combo (SettingCards)."""
from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from qfluentwidgets import (
    ComboBox,
    FluentIcon,
    ScrollArea,
    SettingCard,
    SwitchSettingCard,
    TitleLabel,
    isDarkTheme,
)

from epc_gui.i18n import get_locale, tr
from epc_gui.services import history as hist_svc


class SettingsPage(ScrollArea):
    theme_changed = pyqtSignal(str)   # "light" | "dark"
    locale_changed = pyqtSignal(str)  # "zh" | "en"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settings")
        container = QWidget()
        self.setWidget(container)
        root = QVBoxLayout(container)
        root.setContentsMargins(24, 18, 24, 18)
        root.setSpacing(12)

        self.title = TitleLabel("")
        root.addWidget(self.title)

        # 1.11.3: SwitchSettingCard(icon, title, content=None, configItem=None,
        # parent=None) — pass the parent by keyword, or `self` binds to
        # configItem and the switch crashes on .value.
        self.theme_card = SwitchSettingCard(
            FluentIcon.PALETTE, "", "", parent=self
        )
        self.theme_card.setChecked(isDarkTheme())
        self.theme_card.checkedChanged.connect(self._on_theme_switch)
        root.addWidget(self.theme_card)

        # 1.11.3: ComboBoxSettingCard requires an OptionsConfigItem as its
        # first argument; a plain SettingCard + ComboBox is the documented
        # equivalent without the config bridge (verified in the Task 0 spike).
        self.lang_card = SettingCard(FluentIcon.LANGUAGE, "", "", parent=self)
        self.lang_combo = ComboBox(self.lang_card)
        self.lang_combo.addItems(["中文", "English"])
        self.lang_card.hBoxLayout.addWidget(self.lang_combo)
        self.lang_card.comboBox = self.lang_combo
        self.lang_combo.currentIndexChanged.connect(self._on_lang_combo)
        root.addWidget(self.lang_card)

        root.addStretch(1)
        self.retranslate()
        self.reflect()

    def retranslate(self) -> None:
        self.title.setText(tr("settings.title"))
        self.theme_card.setTitle(tr("settings.dark_card"))
        self.theme_card.setContent(tr("settings.dark_hint"))
        self.lang_card.setTitle(tr("settings.lang_card"))

    def reflect(self) -> None:
        """Sync widget state from persisted settings (shell calls this)."""
        self.theme_card.blockSignals(True)
        self.theme_card.setChecked(isDarkTheme())
        self.theme_card.blockSignals(False)
        self.lang_card.comboBox.blockSignals(True)
        self.lang_card.comboBox.setCurrentIndex(0 if get_locale() == "zh" else 1)
        self.lang_card.comboBox.blockSignals(False)

    def _on_theme_switch(self, dark: bool) -> None:
        self.theme_changed.emit("dark" if dark else "light")

    def _on_lang_combo(self, idx: int) -> None:
        if self.lang_card.comboBox.signalsBlocked():
            return
        self.locale_changed.emit("zh" if idx == 0 else "en")
