"""
Podman Containers
=================
Combiner that unifies root-owned and rootless podman containers into a single
searchable view.
"""

from typing import List, Optional

from insights.core.exceptions import SkipComponent
from insights.core.plugins import combiner
from insights.parsers.podman import (
    PodmanContainerSearch,
    PodmanPsAllJson,
    PodmanPsAllJsonRootless,
)


@combiner(optional=[PodmanPsAllJson, PodmanPsAllJsonRootless])
class PodmanContainers(PodmanContainerSearch):
    """
    Unified view of root-owned and rootless podman containers.

    Attributes:
        data (list): Merged flat list of container dicts (rootful + rootless).

    Raises:
        SkipComponent: When neither source has any containers.
    """

    def __init__(
        self,
        rootful: Optional[PodmanPsAllJson],
        rootless: Optional[PodmanPsAllJsonRootless],
    ) -> None:
        self.data: List[dict] = []
        if rootful:
            self.data.extend(rootful.data)
        if rootless:
            self.data.extend(rootless.data)
        if not self.data:
            raise SkipComponent("No podman containers found")
