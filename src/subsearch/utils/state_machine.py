from dataclasses import dataclass
from enum import Enum, auto


class CoreEnum(Enum):
    UNKNOWN = "unknown"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    SCRAPING_SUBSCENE = "scraping_subscene"
    SCRAPING_OPENSUBTITLES = "scraping_opensubtitles"
    SCRAPING_YIFYSUBTITLES = "scraping_yifysubtitles"
    DOWNLOADING_FILES = "downloading_files"
    EXTRACTING_FILES = "extracting_files"
    CLEANING_UP = "cleaning_up"
    EXITING = "exiting"
    NO_FILE_FOUND = "no_file_found"


class State:
    previous_states: list[Enum] = []

    @classmethod
    def __create__(cls, state: Enum) -> None:
        cls.__state = state

    def set_state(self, state: Enum) -> None:
        self.__state = state
        self.previous_states.append(state)

    @property
    def state(self) -> Enum:
        return self.__state

    @property
    def ran_scrape(self) -> bool:
        scraped = [CoreEnum.SCRAPING_SUBSCENE, CoreEnum.SCRAPING_OPENSUBTITLES, CoreEnum.SCRAPING_YIFYSUBTITLES]
        return any(provider in self.previous_states for provider in scraped)

    @property
    def file_exist(self) -> bool:
        return CoreEnum.NO_FILE_FOUND not in self.previous_states


@dataclass(frozen=True, order=True)
class CoreState(State):
    unknown: CoreEnum = CoreEnum.UNKNOWN
    initializing: CoreEnum = CoreEnum.INITIALIZING
    initialized: CoreEnum = CoreEnum.INITIALIZED
    scraping_subscene: CoreEnum = CoreEnum.SCRAPING_SUBSCENE
    scraping_opensubtitles: CoreEnum = CoreEnum.SCRAPING_OPENSUBTITLES
    scraping_yifysubtitles: CoreEnum = CoreEnum.SCRAPING_YIFYSUBTITLES
    downloading_files: CoreEnum = CoreEnum.DOWNLOADING_FILES
    extracting_files: CoreEnum = CoreEnum.EXTRACTING_FILES
    cleaning_up: CoreEnum = CoreEnum.CLEANING_UP
    exiting: CoreEnum = CoreEnum.EXITING
    no_file_found: CoreEnum = CoreEnum.NO_FILE_FOUND
