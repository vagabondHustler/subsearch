import ctypes
import sys
import tkinter as tk
from dataclasses import dataclass

from src.gui.tooltip import Hovertip
from src.scraper.subscene_soup import get_download_url
from src.utilities.file_manager import (clean_up, download_zip_auto,
                                        extract_zips)
from src.utilities.local_paths import cwd, root_directory
from src.utilities.version import current_version
