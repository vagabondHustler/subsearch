from typing import Any

from subsearch.runtime.models.model import AppConfig


def get_app_config_from_data(data: dict[str, Any]) -> AppConfig:
    return AppConfig(
        selected_language=data["language"]["selected"],
        accept_threshold=data["search"]["accept_threshold"],
        hearing_impaired=data["search"]["hearing_impaired"],
        non_hearing_impaired=data["search"]["non_hearing_impaired"],
        only_foreign_parts=data["search"]["only_foreign_parts"],
        providers=data["search"]["providers"],
        token_weights=data["search"]["token_weights"],
        token_multipliers=data["search"]["token_multipliers"],
        context_menu=data["shell_integration"]["context_menu"],
        context_menu_icon=data["shell_integration"]["context_menu_icon"],
        file_extensions=data["shell_integration"]["file_extensions"],
        system_tray=data["notifications"]["system_tray"],
        summary_notification=data["notifications"]["summary_notification"],
        search_mode=data["download_manager"]["search_mode"],
        manually_handle_post_processing=data["download_manager"]["manually_handle_post_processing"],
        use_post_processing_target=data["download_manager"]["use_post_processing_target"],
        download_manager_target_path=data["download_manager"]["target_path"],
        download_manager_working_directory=data["download_manager"]["working_directory"],
        post_processing=data["post_processing"],
        show_terminal=data["application"]["show_terminal"],
        single_instance=data["application"]["single_instance"],
        api_call_limit=data["network"]["api_call_limit"],
        request_connect_timeout=data["network"]["request_connect_timeout"],
        request_read_timeout=data["network"]["request_read_timeout"],
        diagnostics=data["diagnostics"],
        subsource_api_key_exists=data["credentials"]["subsource"]["api_key_exists"],
        subsource_api_key=data["credentials"]["subsource"]["api_key"],
    )
