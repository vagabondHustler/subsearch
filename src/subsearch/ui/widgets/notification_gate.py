import ctypes

# QUERY_USER_NOTIFICATION_STATE: only this value means the user is present and
# willing to be interrupted; every other value is fullscreen or presentation
# mode, where Windows itself suppresses toasts.
QUNS_ACCEPTS_NOTIFICATIONS = 5


def notifications_allowed() -> bool:
    return not _focus_assist_active() and _user_present()


def _focus_assist_active() -> bool:
    # Win11 Do Not Disturb / Focus reports through ToastNotificationMode; the legacy
    # SHQueryUserNotificationState QUIET_TIME path no longer reflects it reliably.
    from winrt.windows.ui.notifications import (
        ToastNotificationManager,
        ToastNotificationMode,
    )

    try:
        mode = ToastNotificationManager.get_default().notification_mode
    except OSError:
        return False
    return mode != ToastNotificationMode.UNRESTRICTED


def _user_present() -> bool:
    state = ctypes.c_int()
    result = ctypes.windll.shell32.SHQueryUserNotificationState(ctypes.byref(state))
    if result != 0:
        return True
    return state.value == QUNS_ACCEPTS_NOTIFICATIONS
