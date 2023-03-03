    """
    A class used to manage the tabs of a parent widget.

    Args:
        parent: The parent widget.
        tabs (dict[str, Any]): A dictionary containing tabs as a key-value pair. Key is the name of the tab and value is the content of the tab.
        active_tab (str): The current active tab.

    Attributes:
        parent: The parent widget.
        tabs (dict[str, Any]): A dictionary containing tabs as a key-value pair. Key is the name of the tab and value is the content of the tab.
        buttons: A dictionary containing button widgets as a key-value pair. Key is the name of the associated tab and value is the corresponding button widget.
        active_tab (str): The current active tab.

    Methods:
        activate_tabs(): Place the content of the active tab on the parent widget.
        release_tab(event): Called when a tab button is released. Set the active tab and call 'activate_tabs()' method.
        press_tab(event): Called when a tab button is pressed. Bind '<ButtonRelease>' event to the button widget.
        deactivate_tabs(): Hide the content of all tabs except the active one.
        enter_tab(event): Called when mouse enters a tab button. Bind '<ButtonPress>' event to the button widget. 
        leave_tab(event):  Called when mouse leaves a tab button. Unbind '<ButtonPress>' event from the button widget, and call 'activate_tabs()' and 'deactivate_tabs()' methods.
        get_btn(dict_, event_, equals=True): Helper method to retrieve the button widget and its key.
    """
