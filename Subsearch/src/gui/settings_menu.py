        if is_exe_version():
            terminal_var.set(f"Disabled")
            text1 = " "
            text2 = text1
            tip_text1 = "Not available when running .exe-package"
            tip_text2 = tip_text1

        else:
            text1 = "True"
            text2 = "False"
            tip_text1 = "Show the terminal when searching for subtitles\n Everything shown in the terminal is avalible in search.log"
            tip_text2 = "Hide the terminal when searching for subtitles"

        Create.label(
            self, text="Show terminal on search", row=1, col=1, sticky="w", font=Tks.font8b
        )
            text=text1,
            tip_text=tip_text1,
            text=text2,
            tip_text=tip_text2,
        if is_exe_version():
            return
        if is_exe_version():
            return
