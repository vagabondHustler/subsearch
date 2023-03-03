    """Get the path of the PNG file for a given tab.

    Args:
        tab (str): The name of the tab.

    Returns:
        Path: The path of the PNG file for the specified tab.

    Raises:
        None.
    """
    """Calculate the required size of a button based on its content.

    Args:
        cls: The class from which the method is being called.
        width_ (optional): The initial width of the button before calculation. Defaults to 18.
        height_ (optional): The initial height of the button before calculation. Defaults to 2.

    Returns:
        A tuple of integer values representing the calculated width and height of the button
    """

    """
    Calculates the required width of a ttk Checkbutton widget in pixels.

    Args:
        cls (class): The parent class where the Checkbutton will be placed.
        width_ (int, optional): The desired width of the ttk check button. Defaults to 16.

    Returns:
        int: The required width in pixels of a ttk Checkbutton based on its current settings.
    """

    """
    Set the default grid size for a tkinter GUI window.

    Args:
        cls (object): The class object.
        width_ (int, optional): The default width. Defaults to 18.

    Returns:
        None
    """
    """
    Attach an image displayed as a tab onto the application window.

    Args:
        cls (class): The class representing the application.
        img (str): The name of the image file.
        type (str): The type of the image file.
        x (int, optional): The width of the image in pixels. Defaults to 27.
        y (int, optional): The height of the image in pixels. Defaults to 27.
    """
    """
    Updates an asset in a tkinter canvas with the provided image.
    
    Args:
        cls: The canvas instance that houses the current asset.
        img: The image asset to replace the current asset within the canvas.
        x: The X coordinate for positioning of the new asset.
        y: The Y coordinate for positioning of the new asset.
        
    Returns:
        None 
    """
    """
    Sets custom button styles
    
    Args:
        None
    
    Returns:
        None
    """
    """
    A class that creates and manages the positioning of a tkinter frame.

    Args:
        parent: The parent widget.

    Attributes:
        None

    Methods:
        set(w=int, h=int, ws_value_offset=int, hs_value_offset=int, other=bool): Sets the window dimension
            in width and height. It also sets offsets by which to move the window horizontally (ws_value_offset) 
            and vertically (hs_value_offset). If other=True, it allows changing other dimensions not typically 
            touched (eg. height of frame/window title bar)

    Returns:
       None
    """
        """
        Constructor Method for WindowPosition Class

        Args:
            parent: The parent widget.
        """
        """
        Set the size of the current window/Frame

        Args:
             w: An optional integer for setting the width of the window/frame
             h: An optional integer for setting the height of the window/frame
             ws_value_offset: An optional integer for setting the horizontal offset of the window/frame
             hs_value_offset: An optional integer for setting the vertical offset of the window/frame
             other: An optional bool variable to allow changing other dimensions not typically touched 
                    eg. height of frame/window title bar

        Returns:
              None
        """
    """
    A class that initializes a color picker for given string variables.

    Args:
        string_var: A tkinter StringVar object to represent value of the color.
        clabel: A tkinter Label object to represent the color label.
        is_pct: A boolean variable initialized to False indicating if configured level in percentage.

    Attributes:
        string_var: A tkinter StringVar object representing value of the color.
        clabel: A tkinter Label object representing the color label.
        is_pct: A boolean variable to determine percentage threshold.

    Methods:
        pick(): Method to determine and update the color of clabel based on the string_var value.
    """
    """
    A toplevel widget that displays a message when the user hovers over a specified widget

    Args:
        parent (tkinter.Tk): The parent widget
        _widget (tkinter.Widget): The widget to attach the tooltip to
        *_text (str): The text to be displayed in the tooltip
        _background (str): The background color of the tooltip

    Methods:
        show(): Creates and displays a toplevel widget containing the text to be displayed in the tooltip
    """

    """
    A button that toggles a configuration setting on or off.

    Args:
        parent (tk.Widget): The parent widget.
        setting_label (str): Name of the setting to be displayeed.
        config_key (str): Key in the configuration file where the state is stored.
        write_to_reg (bool, optional): Whether to also write the state to registry. Defaults to False.
        show_if_exe (bool, optional): Only show the button if the program is not running from an executable. Defaults to True.
    """
        """
        Function called when the mouse enters the button area.

        Args:
            event: The tkinter event object.
        """
        """
        Function called when the mouse leaves the button area.

        Args:
            event: The tkinter event object.
        """
        """
        Function called when the button is set to True.

        Args:
            event: The tkinter event object.
        """
        """
        Function called when the button is set to False.

        Args:
            event: The tkinter event object.
        """
