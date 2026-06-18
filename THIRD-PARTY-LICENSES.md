# Third-party licenses

Subsearch is licensed under the GNU General Public License v3.0 (or later);
see `LICENSE`.

The Subsearch application also includes the third-party components listed
below. One of them, PySide6-Fluent-Widgets, is licensed under the GPL v3. 
Subsearch as a whole is distributed under the GPL v3. The complete
corresponding source is publicly available at <https://github.com/vagabondHustler/subsearch>.

---

## PySide6 (Qt for Python)

- Component: PySide6, PySide6-Essentials, PySide6-Addons, shiboken6
- License: LGPL v3 (used under the LGPL-3.0 option of its LGPLv3 / GPLv2 / GPLv3 triple license)
- Project: <https://www.qt.io/qt-for-python>
- Source and license text: <https://code.qt.io/cgit/pyside/pyside-setup.git/>

Subsearch links PySide6 dynamically. The Qt libraries are shipped as separate
files (DLLs) and may be replaced by the user with a compatible version, as
required by the LGPL.

## PySide6-Fluent-Widgets

- Component: PySide6-Fluent-Widgets
- License: GPL v3
- Project: <https://qfluentwidgets.com>
- Source and license text: <https://github.com/zhiyiYo/PyQt-Fluent-Widgets/tree/PySide6>

A separate commercial license for this component is offered by its author; see
the project page above.

## Windows-Toasts

- Component: windows-toasts (and its winrt-* runtime dependencies)
- License: Apache License 2.0
- Project: <https://github.com/DatGuy1/Windows-Toasts>
- Source and license text: <https://github.com/DatGuy1/Windows-Toasts>

Used to deliver native Windows notifications. Apache 2.0 is compatible with the
GPL v3 under which Subsearch as a whole is distributed.
