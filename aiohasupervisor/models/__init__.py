"""Models for supervisor client."""

from aiohasupervisor.models.addons import (
    AddonBoot,
    AddonBootConfig,
    AddonsConfigValidate,
    AddonsOptions,
    AddonsSecurityOptions,
    AddonsStats,
    AddonStage,
    AddonStartup,
    AddonState,
    AddonsUninstall,
    AppArmor,
    Capability,
    CpuArch,
    InstalledAddon,
    InstalledAddonComplete,
    Repository,
    StoreAddon,
    StoreAddonComplete,
    StoreAddonUpdate,
    StoreAddRepository,
    StoreInfo,
    SupervisorRole,
)
from aiohasupervisor.models.backups import (
    Backup,
    BackupAddon,
    BackupComplete,
    BackupContent,
    BackupJob,
    BackupsInfo,
    BackupsOptions,
    BackupType,
    DownloadBackupOptions,
    Folder,
    FreezeOptions,
    FullBackupOptions,
    FullRestoreOptions,
    NewBackup,
    PartialBackupOptions,
    PartialRestoreOptions,
    RemoveBackupOptions,
    UploadBackupOptions,
)
from aiohasupervisor.models.discovery import (
    Discovery,
    DiscoveryConfig,
)
from aiohasupervisor.models.homeassistant import (
    HomeAssistantInfo,
    HomeAssistantOptions,
    HomeAssistantRebuildOptions,
    HomeAssistantRestartOptions,
    HomeAssistantStats,
    HomeAssistantStopOptions,
    HomeAssistantUpdateOptions,
)
from aiohasupervisor.models.host import (
    HostInfo,
    HostOptions,
    RebootOptions,
    Service,
    ServiceState,
    ShutdownOptions,
)
from aiohasupervisor.models.mounts import (
    CIFSMountRequest,
    CIFSMountResponse,
    MountCifsVersion,
    MountsInfo,
    MountsOptions,
    MountState,
    MountType,
    MountUsage,
    NFSMountRequest,
    NFSMountResponse,
)
from aiohasupervisor.models.network import (
    AccessPoint,
    AuthMethod,
    DockerNetwork,
    InterfaceMethod,
    InterfaceType,
    IPv4,
    IPv4Config,
    IPv6,
    IPv6Config,
    NetworkInfo,
    NetworkInterface,
    NetworkInterfaceConfig,
    Vlan,
    VlanConfig,
    Wifi,
    WifiConfig,
    WifiMode,
)
from aiohasupervisor.models.os import (
    BootSlot,
    BootSlotName,
    DataDisk,
    GreenInfo,
    GreenOptions,
    MigrateDataOptions,
    OSInfo,
    OSUpdate,
    RaucState,
    SetBootSlotOptions,
    YellowInfo,
    YellowOptions,
)
from aiohasupervisor.models.resolution import (
    Check,
    CheckOptions,
    CheckType,
    ContextType,
    Issue,
    IssueType,
    ResolutionInfo,
    Suggestion,
    SuggestionType,
    UnhealthyReason,
    UnsupportedReason,
)
from aiohasupervisor.models.root import (
    AvailableUpdate,
    HostFeature,
    LogLevel,
    RootInfo,
    SupervisorState,
    UpdateChannel,
    UpdateType,
)
from aiohasupervisor.models.supervisor import (
    SupervisorInfo,
    SupervisorOptions,
    SupervisorStats,
    SupervisorUpdateOptions,
)

__all__ = [
    "HostFeature",
    "SupervisorState",
    "UpdateChannel",
    "LogLevel",
    "UpdateType",
    "RootInfo",
    "AvailableUpdate",
    "AddonStage",
    "AddonStartup",
    "AddonBoot",
    "AddonBootConfig",
    "CpuArch",
    "Capability",
    "AppArmor",
    "SupervisorRole",
    "AddonState",
    "StoreAddon",
    "StoreAddonComplete",
    "InstalledAddon",
    "InstalledAddonComplete",
    "AddonsOptions",
    "AddonsConfigValidate",
    "AddonsSecurityOptions",
    "AddonsStats",
    "AddonsUninstall",
    "Repository",
    "StoreInfo",
    "StoreAddonUpdate",
    "StoreAddRepository",
    "Check",
    "CheckOptions",
    "CheckType",
    "ContextType",
    "Issue",
    "IssueType",
    "ResolutionInfo",
    "Suggestion",
    "SuggestionType",
    "UnhealthyReason",
    "UnsupportedReason",
    "SupervisorInfo",
    "SupervisorOptions",
    "SupervisorStats",
    "SupervisorUpdateOptions",
    "HomeAssistantInfo",
    "HomeAssistantOptions",
    "HomeAssistantRebuildOptions",
    "HomeAssistantRestartOptions",
    "HomeAssistantStats",
    "HomeAssistantStopOptions",
    "HomeAssistantUpdateOptions",
    "RaucState",
    "BootSlotName",
    "BootSlot",
    "OSInfo",
    "OSUpdate",
    "MigrateDataOptions",
    "DataDisk",
    "SetBootSlotOptions",
    "GreenInfo",
    "GreenOptions",
    "YellowInfo",
    "YellowOptions",
    "Backup",
    "BackupAddon",
    "BackupComplete",
    "BackupContent",
    "BackupJob",
    "BackupsInfo",
    "BackupsOptions",
    "BackupType",
    "DownloadBackupOptions",
    "Folder",
    "FreezeOptions",
    "FullBackupOptions",
    "FullRestoreOptions",
    "NewBackup",
    "PartialBackupOptions",
    "PartialRestoreOptions",
    "RemoveBackupOptions",
    "UploadBackupOptions",
    "Discovery",
    "DiscoveryConfig",
    "AccessPoint",
    "AuthMethod",
    "DockerNetwork",
    "InterfaceMethod",
    "InterfaceType",
    "IPv4",
    "IPv4Config",
    "IPv6",
    "IPv6Config",
    "NetworkInfo",
    "NetworkInterface",
    "NetworkInterfaceConfig",
    "Vlan",
    "VlanConfig",
    "Wifi",
    "WifiConfig",
    "WifiMode",
    "HostInfo",
    "HostOptions",
    "RebootOptions",
    "Service",
    "ServiceState",
    "ShutdownOptions",
    "CIFSMountRequest",
    "CIFSMountResponse",
    "MountCifsVersion",
    "MountsInfo",
    "MountsOptions",
    "MountState",
    "MountType",
    "MountUsage",
    "NFSMountRequest",
    "NFSMountResponse",
]
