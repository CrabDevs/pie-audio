import typing

from pieapp.structs.plugins import Plugins

from piekit.plugins.base import PiePlugin
from piekit.managers.assets.mixins import AssetsAccessor
from piekit.managers.configs.mixins import ConfigAccessor
from piekit.managers.locales.mixins import LocalesAccessor


class TestPlugin(
    PiePlugin,
    ConfigAccessor,
    LocalesAccessor,
    AssetsAccessor,
):
    name = Plugins.TestPlugin
    section = Plugins.TestPlugin

    def init(self) -> None:
        self.logger.info(self.getConfig("config.key"))
        self.logger.info(self.getTranslation("Test String"))
        self.logger.info(self.getAsset("cancel.png"))


def main(*args, **kwargs) -> typing.Any:
    return TestPlugin(*args, **kwargs)
