from typing import Union
from piekit.managers.structs import Section
from piekit.managers.registry import Managers
from piekit.managers.structs import SysManager


def translate(text: str, section: Section.Shared = Section.Shared) -> str:
    return Managers(SysManager.Locales).get(section, text)


def get_translation_scope(section: Union[str, Section] = Section.Shared) -> dict[str, str]:
    return Managers(SysManager.Locales).get_section(section)


getTranslationSection = get_translation_scope