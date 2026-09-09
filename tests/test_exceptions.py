"""Tests for error_key to exception class mapping."""

from json import dumps

from aiointercept import aiointercept
import pytest

from aiohasupervisor import SupervisorClient
from aiohasupervisor.exceptions import (
    AddonNotSupportedArchitectureError,
    AddonNotSupportedHomeAssistantVersionError,
    AddonNotSupportedMachineTypeError,
    AppAlreadyInstalledError,
    AppBackupMetadataInvalidError,
    AppBootConfigCannotChangeError,
    AppBuildArchitectureNotSupportedError,
    AppBuildDockerfileMissingError,
    AppBuildFailedUnknownError,
    AppConfigurationInvalidError,
    AppFileReadError,
    AppNotFoundError,
    AppNotInstalledError,
    AppNotInStoreError,
    AppNotRunningError,
    AppNotSupportedArchitectureError,
    AppNotSupportedHomeAssistantVersionError,
    AppNotSupportedMachineTypeError,
    AppNotSupportedWriteStdinError,
    AppNoUpdateAvailableError,
    AppPortConflictError,
    AppPrePostBackupCommandReturnedError,
    AppRebuildImageBasedError,
    AppRebuildVersionChangedError,
    AppStatsTimeoutError,
    AppUnknownError,
    AudioNotRunningError,
    AudioStatsTimeoutError,
    AudioUnknownError,
    AuthHomeAssistantAPIValidationError,
    AuthInvalidNonStringValueError,
    AuthListUsersError,
    AuthPasswordResetError,
    BackupMountDownError,
    BackupRestoreUnknownError,
    CliNotRunningError,
    CliStatsTimeoutError,
    CliUnknownError,
    CoreDNSNotRunningError,
    CoreDNSStatsTimeoutError,
    CoreDNSUnknownError,
    DockerContainerNotFoundError,
    DockerContainerNotRunningError,
    DockerContainerPortConflictError,
    DockerHubRateLimitExceededError,
    DockerNoSpaceOnDeviceError,
    DockerRegistryAuthError,
    DockerRegistryRateLimitExceededError,
    DockerStatsTimeoutError,
    DockerStatsUnknownError,
    GithubContainerRegistryRateLimitExceededError,
    HomeAssistantNotRunningError,
    HomeAssistantStatsTimeoutError,
    HomeAssistantUnknownError,
    HomeAssistantUpdateAlreadyInstalledError,
    HomeAssistantUpdateError,
    HomeAssistantUpdateImageError,
    HostContainerLogEpochError,
    HostInvalidHostnameError,
    MountActivationError,
    MountNotFoundError,
    MountReloadError,
    MountSetupError,
    MountTargetNotDirectoryError,
    MountTargetNotEmptyError,
    MountUnmountError,
    MountUsageNotMountedError,
    MountUsageReadError,
    MountUsageTimeoutError,
    MulticastNotRunningError,
    MulticastStatsTimeoutError,
    MulticastUnknownError,
    ObserverNotRunningError,
    ObserverPortConflictError,
    ObserverStatsTimeoutError,
    ObserverUnknownError,
    ResolutionCheckNotFoundError,
    ResolutionIssueNotFoundError,
    ResolutionSuggestionNotFoundError,
    ServiceAlreadyProvidedError,
    ServiceNotProvidedError,
    StoreAppNotFoundError,
    StoreRepositoryAlreadyAddedError,
    StoreRepositoryLocalCannotResetError,
    StoreRepositoryUnknownError,
    SupervisorError,
    SupervisorStatsTimeoutError,
    SupervisorUnknownError,
)

from .const import SUPERVISOR_URL

# Hard-coded mapping of every error_key Supervisor may send to the exception
# class it must raise. This is intentionally NOT derived from
# aiohasupervisor.exceptions.ERROR_KEYS: the point of this test is to catch an
# incompatible change to that registry (a key repointed to a different class,
# a key removed, etc.) as a compatibility break, so it needs its own
# independent expectation of what the mapping should be.
EXPECTED_ERROR_KEY_CLASSES: dict[str, type[SupervisorError]] = {
    "addon_not_supported_architecture_error": AddonNotSupportedArchitectureError,
    "addon_not_supported_home_assistant_version_error": (
        AddonNotSupportedHomeAssistantVersionError
    ),
    "addon_not_supported_machine_type_error": AddonNotSupportedMachineTypeError,
    "app_already_installed_error": AppAlreadyInstalledError,
    "app_backup_metadata_invalid_error": AppBackupMetadataInvalidError,
    "app_boot_config_cannot_change_error": AppBootConfigCannotChangeError,
    "app_build_architecture_not_supported_error": (
        AppBuildArchitectureNotSupportedError
    ),
    "app_build_dockerfile_missing_error": AppBuildDockerfileMissingError,
    "app_build_failed_unknown_error": AppBuildFailedUnknownError,
    "app_configuration_invalid_error": AppConfigurationInvalidError,
    "app_file_read_error": AppFileReadError,
    "app_no_update_available_error": AppNoUpdateAvailableError,
    "app_not_found_error": AppNotFoundError,
    "app_not_in_store_error": AppNotInStoreError,
    "app_not_installed_error": AppNotInstalledError,
    "app_not_running_error": AppNotRunningError,
    "app_not_supported_architecture_error": AppNotSupportedArchitectureError,
    "app_not_supported_home_assistant_version_error": (
        AppNotSupportedHomeAssistantVersionError
    ),
    "app_not_supported_machine_type_error": AppNotSupportedMachineTypeError,
    "app_not_supported_write_stdin_error": AppNotSupportedWriteStdinError,
    "app_port_conflict": AppPortConflictError,
    "app_pre_post_backup_command_returned_error": (
        AppPrePostBackupCommandReturnedError
    ),
    "app_rebuild_image_based_error": AppRebuildImageBasedError,
    "app_rebuild_version_changed_error": AppRebuildVersionChangedError,
    "app_stats_timeout_error": AppStatsTimeoutError,
    "app_unknown_error": AppUnknownError,
    "audio_not_running_error": AudioNotRunningError,
    "audio_stats_timeout_error": AudioStatsTimeoutError,
    "audio_unknown_error": AudioUnknownError,
    "auth_home_assistant_api_validation_error": AuthHomeAssistantAPIValidationError,
    "auth_invalid_non_string_value_error": AuthInvalidNonStringValueError,
    "auth_list_users_error": AuthListUsersError,
    "auth_password_reset_error": AuthPasswordResetError,
    "backup_mount_down": BackupMountDownError,
    "backup_restore_unknown_error": BackupRestoreUnknownError,
    "cli_not_running_error": CliNotRunningError,
    "cli_stats_timeout_error": CliStatsTimeoutError,
    "cli_unknown_error": CliUnknownError,
    "container_registry_rate_limit_exceeded": DockerRegistryRateLimitExceededError,
    "coredns_not_running_error": CoreDNSNotRunningError,
    "coredns_stats_timeout_error": CoreDNSStatsTimeoutError,
    "coredns_unknown_error": CoreDNSUnknownError,
    "docker_container_not_found_error": DockerContainerNotFoundError,
    "docker_container_not_running_error": DockerContainerNotRunningError,
    "docker_container_port_conflict": DockerContainerPortConflictError,
    "docker_no_space_on_device": DockerNoSpaceOnDeviceError,
    "docker_registry_auth_error": DockerRegistryAuthError,
    "docker_stats_timeout_error": DockerStatsTimeoutError,
    "docker_stats_unknown_error": DockerStatsUnknownError,
    "dockerhub_rate_limit_exceeded": DockerHubRateLimitExceededError,
    "ghcr_rate_limit_exceeded": GithubContainerRegistryRateLimitExceededError,
    "homeassistant_not_running_error": HomeAssistantNotRunningError,
    "homeassistant_stats_timeout_error": HomeAssistantStatsTimeoutError,
    "homeassistant_unknown_error": HomeAssistantUnknownError,
    "homeassistant_update_already_installed_error": (
        HomeAssistantUpdateAlreadyInstalledError
    ),
    "homeassistant_update_error": HomeAssistantUpdateError,
    "homeassistant_update_image_error": HomeAssistantUpdateImageError,
    "host_container_log_epoch_error": HostContainerLogEpochError,
    "host_invalid_hostname": HostInvalidHostnameError,
    "mount_activation_error": MountActivationError,
    "mount_not_found_error": MountNotFoundError,
    "mount_reload_error": MountReloadError,
    "mount_setup_error": MountSetupError,
    "mount_target_not_directory_error": MountTargetNotDirectoryError,
    "mount_target_not_empty_error": MountTargetNotEmptyError,
    "mount_unmount_error": MountUnmountError,
    "mount_usage_not_mounted_error": MountUsageNotMountedError,
    "mount_usage_read_error": MountUsageReadError,
    "mount_usage_timeout_error": MountUsageTimeoutError,
    "multicast_not_running_error": MulticastNotRunningError,
    "multicast_stats_timeout_error": MulticastStatsTimeoutError,
    "multicast_unknown_error": MulticastUnknownError,
    "observer_not_running_error": ObserverNotRunningError,
    "observer_port_conflict": ObserverPortConflictError,
    "observer_stats_timeout_error": ObserverStatsTimeoutError,
    "observer_unknown_error": ObserverUnknownError,
    "resolution_check_not_found_error": ResolutionCheckNotFoundError,
    "resolution_issue_not_found_error": ResolutionIssueNotFoundError,
    "resolution_suggestion_not_found_error": ResolutionSuggestionNotFoundError,
    "service_already_provided_error": ServiceAlreadyProvidedError,
    "service_not_provided_error": ServiceNotProvidedError,
    "store_app_not_found_error": StoreAppNotFoundError,
    "store_repository_already_added_error": StoreRepositoryAlreadyAddedError,
    "store_repository_local_cannot_reset": StoreRepositoryLocalCannotResetError,
    "store_repository_unknown_error": StoreRepositoryUnknownError,
    "supervisor_stats_timeout_error": SupervisorStatsTimeoutError,
    "supervisor_unknown_error": SupervisorUnknownError,
}

_SORTED_ERROR_KEYS = sorted(EXPECTED_ERROR_KEY_CLASSES.items())


@pytest.mark.parametrize(
    ("error_key", "exc_type"),
    _SORTED_ERROR_KEYS,
    ids=[key for key, _ in _SORTED_ERROR_KEYS],
)
async def test_error_key_maps_to_exception_type(
    responses: aiointercept,
    supervisor_client: SupervisorClient,
    error_key: str,
    exc_type: type[SupervisorError],
) -> None:
    """Test each known error_key raises its expected exception type."""
    extra_fields = {"some_field": "some_value"}
    message = f"Test message for {error_key}"
    body = dumps(
        {
            "result": "error",
            "message": message,
            "error_key": error_key,
            "extra_fields": extra_fields,
            "job_id": "test-job-id",
        }
    )
    responses.get(f"{SUPERVISOR_URL}/test", status=400, body=body)

    with pytest.raises(exc_type) as exc_info:
        await supervisor_client._client.get("test")

    err = exc_info.value
    assert type(err) is exc_type
    assert err.error_key == error_key
    assert err.extra_fields == extra_fields
    assert err.job_id == "test-job-id"
    assert str(err) == message


@pytest.mark.parametrize(
    ("error_key", "exc_type"),
    _SORTED_ERROR_KEYS,
    ids=[key for key, _ in _SORTED_ERROR_KEYS],
)
def test_error_key_class_attribute_matches_expectation(
    error_key: str, exc_type: type[SupervisorError]
) -> None:
    """Test each exception class's error_key attribute matches expectation."""
    assert exc_type.error_key == error_key
    assert issubclass(exc_type, SupervisorError)
