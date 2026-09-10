"""Exceptions from supervisor client."""

from abc import ABC
from collections.abc import Callable
from typing import Any


class SupervisorError(Exception):
    """Generic exception."""

    error_key: str | None = None

    def __init__(
        self,
        message: str | None = None,
        extra_fields: dict[str, Any] | None = None,
        job_id: str | None = None,
    ) -> None:
        """Initialize exception."""
        if message is not None:
            super().__init__(message)
        else:
            super().__init__()

        self.job_id = job_id
        self.extra_fields = extra_fields


ERROR_KEYS: dict[str, type[SupervisorError]] = {}


def error_key(
    key: str,
) -> Callable[[type[SupervisorError]], type[SupervisorError]]:
    """Store exception in keyed error map."""

    def wrap(cls: type[SupervisorError]) -> type[SupervisorError]:
        ERROR_KEYS[key] = cls
        cls.error_key = key
        return cls

    return wrap


class SupervisorConnectionError(SupervisorError, ConnectionError):
    """Unknown error connecting to supervisor."""


class SupervisorTimeoutError(SupervisorError, TimeoutError):
    """Timeout connecting to supervisor."""


class SupervisorBadRequestError(SupervisorError):
    """Invalid request made to supervisor."""


class SupervisorAuthenticationError(SupervisorError):
    """Invalid authentication sent to supervisor."""


class SupervisorForbiddenError(SupervisorError):
    """Client is not allowed to take the action requested."""


class SupervisorNotFoundError(SupervisorError):
    """Requested resource does not exist."""


class SupervisorServiceUnavailableError(SupervisorError):
    """Cannot complete request because a required service is unavailable."""


class SupervisorResponseError(SupervisorError):
    """Unusable response received from Supervisor with the wrong type or encoding."""


class AddonNotSupportedError(SupervisorError, ABC):
    """Addon is not supported on this system."""


@error_key("addon_not_supported_architecture_error")
class AddonNotSupportedArchitectureError(
    AddonNotSupportedError, SupervisorBadRequestError
):
    """Addon is not supported on this system due to its architecture."""


@error_key("addon_not_supported_machine_type_error")
class AddonNotSupportedMachineTypeError(
    AddonNotSupportedError, SupervisorBadRequestError
):
    """Addon is not supported on this system due to its machine type."""


@error_key("addon_not_supported_home_assistant_version_error")
class AddonNotSupportedHomeAssistantVersionError(
    AddonNotSupportedError, SupervisorBadRequestError
):
    """Addon is not supported on this system due to its version of Home Assistant."""


# Supervisor sends these three under the legacy "addon_" keys above for v1
# clients (see Supervisor's `_V1_LEGACY_ERROR_KEY_MAP`). These "app_" keyed
# variants mirror Supervisor's current naming and inherit from their legacy
# equivalent to ease a future transition to v2.
@error_key("app_not_supported_architecture_error")
class AppNotSupportedArchitectureError(AddonNotSupportedArchitectureError):
    """App is not supported on this system due to its architecture."""


@error_key("app_not_supported_machine_type_error")
class AppNotSupportedMachineTypeError(AddonNotSupportedMachineTypeError):
    """App is not supported on this system due to its machine type."""


@error_key("app_not_supported_home_assistant_version_error")
class AppNotSupportedHomeAssistantVersionError(
    AddonNotSupportedHomeAssistantVersionError
):
    """App is not supported on this system due to its version of Home Assistant."""


class HomeAssistantError(SupervisorError, ABC):
    """Error related to Home Assistant."""


@error_key("homeassistant_update_error")
class HomeAssistantUpdateError(HomeAssistantError, SupervisorBadRequestError):
    """Raised when updating Home Assistant failed."""


@error_key("homeassistant_update_image_error")
class HomeAssistantUpdateImageError(HomeAssistantUpdateError):
    """Raised when the Home Assistant image cannot be downloaded during update."""


@error_key("homeassistant_update_already_installed_error")
class HomeAssistantUpdateAlreadyInstalledError(HomeAssistantUpdateError):
    """Raised when the requested Home Assistant version is already installed."""


@error_key("homeassistant_not_running_error")
class HomeAssistantNotRunningError(HomeAssistantError, SupervisorBadRequestError):
    """Raised when Home Assistant is not running."""


@error_key("homeassistant_stats_timeout_error")
class HomeAssistantStatsTimeoutError(HomeAssistantError):
    """Raised when fetching stats for Home Assistant times out."""


@error_key("homeassistant_unknown_error")
class HomeAssistantUnknownError(HomeAssistantError):
    """Raised when an unknown error occurs with Home Assistant."""


@error_key("supervisor_unknown_error")
class SupervisorUnknownError(SupervisorError):
    """Raised when an unknown error occurs with Supervisor or its container."""


@error_key("supervisor_stats_timeout_error")
class SupervisorStatsTimeoutError(SupervisorError):
    """Raised when fetching stats for Supervisor times out."""


class CliError(SupervisorError, ABC):
    """Error related to the HA cli plugin."""


@error_key("cli_not_running_error")
class CliNotRunningError(CliError, SupervisorBadRequestError):
    """Raised when the HA cli plugin is not running."""


@error_key("cli_stats_timeout_error")
class CliStatsTimeoutError(CliError):
    """Raised when fetching stats for the HA cli plugin times out."""


@error_key("cli_unknown_error")
class CliUnknownError(CliError):
    """Raised when an unknown error occurs getting stats for the HA cli plugin."""


class ObserverError(SupervisorError, ABC):
    """Error related to the Observer plugin."""


@error_key("observer_port_conflict")
class ObserverPortConflictError(ObserverError, SupervisorBadRequestError):
    """Raised if Observer cannot start due to a port conflict."""


@error_key("observer_not_running_error")
class ObserverNotRunningError(ObserverError, SupervisorBadRequestError):
    """Raised when Observer is not running."""


@error_key("observer_stats_timeout_error")
class ObserverStatsTimeoutError(ObserverError):
    """Raised when fetching stats for Observer times out."""


@error_key("observer_unknown_error")
class ObserverUnknownError(ObserverError):
    """Raised when an unknown error occurs getting stats for Observer."""


class MulticastError(SupervisorError, ABC):
    """Error related to the Multicast plugin."""


@error_key("multicast_not_running_error")
class MulticastNotRunningError(MulticastError, SupervisorBadRequestError):
    """Raised when Multicast is not running."""


@error_key("multicast_stats_timeout_error")
class MulticastStatsTimeoutError(MulticastError):
    """Raised when fetching stats for Multicast times out."""


@error_key("multicast_unknown_error")
class MulticastUnknownError(MulticastError):
    """Raised when an unknown error occurs getting stats for Multicast."""


class CoreDNSError(SupervisorError, ABC):
    """Error related to the CoreDNS plugin."""


@error_key("coredns_not_running_error")
class CoreDNSNotRunningError(CoreDNSError, SupervisorBadRequestError):
    """Raised when CoreDNS is not running."""


@error_key("coredns_stats_timeout_error")
class CoreDNSStatsTimeoutError(CoreDNSError):
    """Raised when fetching stats for CoreDNS times out."""


@error_key("coredns_unknown_error")
class CoreDNSUnknownError(CoreDNSError):
    """Raised when an unknown error occurs getting stats for CoreDNS."""


class AudioError(SupervisorError, ABC):
    """Error related to the Audio plugin."""


@error_key("audio_not_running_error")
class AudioNotRunningError(AudioError, SupervisorBadRequestError):
    """Raised when Audio is not running."""


@error_key("audio_stats_timeout_error")
class AudioStatsTimeoutError(AudioError):
    """Raised when fetching stats for Audio times out."""


@error_key("audio_unknown_error")
class AudioUnknownError(AudioError):
    """Raised when an unknown error occurs getting stats for Audio."""


class AppError(SupervisorError, ABC):
    """Error related to an App."""


@error_key("app_already_installed_error")
class AppAlreadyInstalledError(AppError, SupervisorBadRequestError):
    """Raised when attempting to install an app that is already installed."""


@error_key("app_not_found_error")
class AppNotFoundError(AppError, SupervisorBadRequestError):
    """Raised when an app cannot be found in any store."""


@error_key("app_not_installed_error")
class AppNotInstalledError(AppError, SupervisorBadRequestError):
    """Raised when an action is taken on an app that is not installed."""


@error_key("app_not_in_store_error")
class AppNotInStoreError(AppError, SupervisorBadRequestError):
    """Raised when an installed app is no longer available in its store."""


@error_key("app_no_update_available_error")
class AppNoUpdateAvailableError(AppError, SupervisorBadRequestError):
    """Raised when an update is requested but local matches store version."""


@error_key("app_rebuild_version_changed_error")
class AppRebuildVersionChangedError(AppError, SupervisorBadRequestError):
    """Raised when rebuild is requested but local and store versions differ."""


@error_key("app_configuration_invalid_error")
class AppConfigurationInvalidError(AppError, SupervisorBadRequestError):
    """Raised if invalid configuration provided for app."""


@error_key("app_boot_config_cannot_change_error")
class AppBootConfigCannotChangeError(AppError, SupervisorBadRequestError):
    """Raised if user attempts to change app boot config when it can't be changed."""


@error_key("app_not_running_error")
class AppNotRunningError(AppError, SupervisorBadRequestError):
    """Raised when an app is not running."""


@error_key("app_stats_timeout_error")
class AppStatsTimeoutError(AppError):
    """Raised when fetching stats for an app times out."""


@error_key("app_port_conflict")
class AppPortConflictError(AppError, SupervisorBadRequestError):
    """Raised if app cannot start due to a port conflict."""


@error_key("app_rebuild_image_based_error")
class AppRebuildImageBasedError(AppError, SupervisorBadRequestError):
    """Raised when rebuild is requested for an image-based app."""


@error_key("app_not_supported_write_stdin_error")
class AppNotSupportedWriteStdinError(AppError, SupervisorBadRequestError):
    """Raised when an app does not support writing to stdin."""


@error_key("app_build_dockerfile_missing_error")
class AppBuildDockerfileMissingError(AppError, SupervisorBadRequestError):
    """Raised when app build is invalid because dockerfile is missing."""


@error_key("app_build_architecture_not_supported_error")
class AppBuildArchitectureNotSupportedError(AppError, SupervisorBadRequestError):
    """Raised when app cannot be built on system due to unsupported architecture."""


@error_key("app_unknown_error")
class AppUnknownError(AppError):
    """Raised when an unknown error occurs taking an action for an app."""


@error_key("app_build_failed_unknown_error")
class AppBuildFailedUnknownError(AppError):
    """Raised when the build failed for an app due to an unknown error."""


@error_key("app_file_read_error")
class AppFileReadError(AppError, SupervisorBadRequestError):
    """Raised when an app metadata file cannot be read due to a filesystem error."""


class AuthError(SupervisorError, ABC):
    """Error related to authentication."""


@error_key("auth_password_reset_error")
class AuthPasswordResetError(AuthError, SupervisorBadRequestError):
    """Raised if password reset failed."""


@error_key("auth_list_users_error")
class AuthListUsersError(AuthError):
    """Raised if listing users failed."""


@error_key("auth_invalid_non_string_value_error")
class AuthInvalidNonStringValueError(AuthError, SupervisorAuthenticationError):
    """Raised if something besides a string provided as username or password."""


@error_key("auth_home_assistant_api_validation_error")
class AuthHomeAssistantAPIValidationError(AuthError):
    """Raised when validating auth details via Home Assistant API fails."""


class HostError(SupervisorError, ABC):
    """Error related to the host."""


@error_key("host_container_log_epoch_error")
class HostContainerLogEpochError(HostError):
    """Raised when the container log epoch cannot be determined via journald."""


@error_key("host_invalid_hostname")
class HostInvalidHostnameError(HostError, SupervisorBadRequestError):
    """Raised when a hostname is rejected by the host as semantically invalid."""


class ServiceError(SupervisorError, ABC):
    """Error related to a discovery service."""


@error_key("service_already_provided_error")
class ServiceAlreadyProvidedError(ServiceError):
    """Raised when a service is already provided by another app."""


@error_key("service_not_provided_error")
class ServiceNotProvidedError(ServiceError, SupervisorNotFoundError):
    """Raised when a service is not currently provided by any app."""


class DockerError(SupervisorError, ABC):
    """Error related to Docker."""


@error_key("docker_container_not_found_error")
class DockerContainerNotFoundError(DockerError, SupervisorNotFoundError):
    """Raised when a referenced container could not be found."""


@error_key("docker_container_not_running_error")
class DockerContainerNotRunningError(DockerError, SupervisorBadRequestError):
    """Raised when an action requires a container to be running but it isn't."""


@error_key("docker_stats_timeout_error")
class DockerStatsTimeoutError(DockerError):
    """Raised when fetching stats for a container times out."""


@error_key("docker_stats_unknown_error")
class DockerStatsUnknownError(DockerError):
    """Raised when an unknown error occurs getting stats for a container."""


@error_key("docker_no_space_on_device")
class DockerNoSpaceOnDeviceError(DockerError, SupervisorBadRequestError):
    """Raised if a docker pull fails due to available space."""


@error_key("docker_container_port_conflict")
class DockerContainerPortConflictError(DockerError, SupervisorBadRequestError):
    """Raised if docker cannot start a container due to a port conflict."""


@error_key("docker_registry_auth_error")
class DockerRegistryAuthError(DockerError, SupervisorBadRequestError):
    """Raised when Docker registry authentication fails."""


@error_key("container_registry_rate_limit_exceeded")
class DockerRegistryRateLimitExceededError(DockerError):
    """Raised when a container registry rate limits requests."""


@error_key("dockerhub_rate_limit_exceeded")
class DockerHubRateLimitExceededError(DockerRegistryRateLimitExceededError):
    """Raised for Docker Hub rate limit exceeded error."""


@error_key("ghcr_rate_limit_exceeded")
class GithubContainerRegistryRateLimitExceededError(
    DockerRegistryRateLimitExceededError
):
    """Raised for GitHub Container Registry rate limit exceeded error."""


class ResolutionError(SupervisorError, ABC):
    """Error related to resolution checks, issues and suggestions."""


@error_key("resolution_check_not_found_error")
class ResolutionCheckNotFoundError(ResolutionError, SupervisorNotFoundError):
    """Raised if check does not exist."""


@error_key("resolution_issue_not_found_error")
class ResolutionIssueNotFoundError(ResolutionError, SupervisorNotFoundError):
    """Raised if issue does not exist."""


@error_key("resolution_suggestion_not_found_error")
class ResolutionSuggestionNotFoundError(ResolutionError, SupervisorNotFoundError):
    """Raised if suggestion does not exist."""


class StoreError(SupervisorError, ABC):
    """Error related to the app store."""


@error_key("store_app_not_found_error")
class StoreAppNotFoundError(StoreError, SupervisorNotFoundError):
    """Raised if a requested app is not in the store."""


@error_key("store_repository_already_added_error")
class StoreRepositoryAlreadyAddedError(StoreError):
    """Raised when a repository is already added to the store."""


@error_key("store_repository_local_cannot_reset")
class StoreRepositoryLocalCannotResetError(StoreError, SupervisorBadRequestError):
    """Raised if user requests a reset on the local app repository."""


@error_key("store_repository_unknown_error")
class StoreRepositoryUnknownError(StoreError):
    """Raised when unknown error occurs taking an action for a store repository."""


class BackupError(SupervisorError, ABC):
    """Error related to backups."""


@error_key("backup_mount_down")
class BackupMountDownError(BackupError, SupervisorBadRequestError):
    """Raised if mount specified for backup is down."""


@error_key("app_backup_metadata_invalid_error")
class AppBackupMetadataInvalidError(BackupError, SupervisorBadRequestError):
    """Raised if invalid metadata file provided for app in backup."""


@error_key("app_pre_post_backup_command_returned_error")
class AppPrePostBackupCommandReturnedError(BackupError, SupervisorBadRequestError):
    """Raised when an app's pre/post backup command returns an error."""


@error_key("backup_restore_unknown_error")
class BackupRestoreUnknownError(BackupError):
    """Raised when an unknown error occurs during backup or restore."""


class MountError(SupervisorError, ABC):
    """Error related to mounting/unmounting."""


@error_key("mount_activation_error")
class MountActivationError(MountError, SupervisorBadRequestError):
    """Raised on mount not reaching active state after mount/reload."""


@error_key("mount_setup_error")
class MountSetupError(MountError, SupervisorBadRequestError):
    """Raised when the systemd units of a mount could not be set up."""


@error_key("mount_unmount_error")
class MountUnmountError(MountError, SupervisorBadRequestError):
    """Raised when a mount could not be removed from the system."""


@error_key("mount_reload_error")
class MountReloadError(MountError, SupervisorBadRequestError):
    """Raised when a mount could not be reloaded."""


class MountInvalidError(MountError, ABC):
    """Error related to an invalid mount attempt."""


@error_key("mount_target_not_directory_error")
class MountTargetNotDirectoryError(MountInvalidError, SupervisorBadRequestError):
    """Raised when a mount target exists but is not a directory."""


@error_key("mount_target_not_empty_error")
class MountTargetNotEmptyError(MountInvalidError, SupervisorBadRequestError):
    """Raised when a mount target directory contains existing data."""


@error_key("mount_not_found_error")
class MountNotFoundError(MountError, SupervisorNotFoundError):
    """Raised when a mount does not exist."""


@error_key("mount_usage_not_mounted_error")
class MountUsageNotMountedError(MountError, SupervisorBadRequestError):
    """Raised when a mount's path is no longer a mount point."""


@error_key("mount_usage_read_error")
class MountUsageReadError(MountError, SupervisorBadRequestError):
    """Raised when reading a mount's storage usage fails."""


@error_key("mount_usage_timeout_error")
class MountUsageTimeoutError(MountError, SupervisorBadRequestError):
    """Raised when a caller gives up waiting on a mount's storage usage probe."""
