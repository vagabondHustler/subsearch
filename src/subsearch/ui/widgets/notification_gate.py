import ctypes

# QUERY_USER_NOTIFICATION_STATE: only this value means the user is present and
# willing to be interrupted; every other value is Focus Assist, fullscreen, or
# presentation mode, where Windows itself suppresses toasts.
QUNS_ACCEPTS_NOTIFICATIONS = 5


def notifications_allowed() -> bool:
    state = ctypes.c_int()
    result = ctypes.windll.shell32.SHQueryUserNotificationState(ctypes.byref(state))
    if result != 0:
        return True
    return state.value == QUNS_ACCEPTS_NOTIFICATIONS
