#!/usr/bin/python

# copyright (c) 2025, Alex Welsh
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: container_repositories
short_description: Manage multiple container repositories of a pulp api server instance
description:
  - "This performs CRUD operations on multiple container repositories in a pulp api server instance in a single call."
options:
  repositories:
    description:
      - List of repositories to manage
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Name of the repository
        type: str
        required: true
      description:
        description:
          - Description of the repository
        type: str
      state:
        description:
          - Desired state of the repository
        type: str
        choices: ["present", "absent"]
        default: present
  concurrency:
    description:
      - Maximum number of concurrent API requests
    type: int
    default: 10
extends_documentation_fragment:
  - pulp.squeezer.pulp
author:
  - Alex Welsh (@alex-welsh)
"""

EXAMPLES = r"""
- name: Create multiple container repositories
  pulp.squeezer.container_repositories:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
    repositories:
      - name: repo1
        description: A brand new repository
        state: present
      - name: repo2
        description: Another repository
        state: present

- name: Create multiple container repositories with custom concurrency
  pulp.squeezer.container_repositories:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
    concurrency: 5
    repositories:
      - name: repo1
        description: A brand new repository
      - name: repo2
        description: Another repository

- name: Delete multiple container repositories
  pulp.squeezer.container_repositories:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
    repositories:
      - name: repo1
        state: absent
      - name: repo2
        state: absent
"""

RETURN = r"""
  repositories:
    description: List of container repository results
    type: list
    returned: always
    elements: dict
    contains:
      name:
        description: Name of the repository
        type: str
      repository:
        description: Repository details (when applicable)
        type: dict
      changed:
        description: Whether the repository was changed
        type: bool
      failed:
        description: Whether the operation failed
        type: bool
      msg:
        description: Error message if failed
        type: str
"""


import traceback

from ansible_collections.pulp.squeezer.plugins.module_utils.pulp_glue import (
    PulpBatchEntityAnsibleModule,
)

try:
    from pulp_glue.container.context import PulpContainerRepositoryContext

    PULP_GLUE_IMPORT_ERR = None
except ImportError:
    PULP_GLUE_IMPORT_ERR = traceback.format_exc()
    PulpContainerRepositoryContext = None


def main():
    with PulpBatchEntityAnsibleModule(
        context_class=PulpContainerRepositoryContext,
        entity_singular="repository",
        entity_plural="repositories",
        entity_attributes=["description"],
        import_errors=[("pulp-glue", PULP_GLUE_IMPORT_ERR)],
        argument_spec={
            "repositories": {
                "type": "list",
                "elements": "dict",
                "options": {
                    "name": {"required": True},
                    "description": {},
                    "state": {"choices": ["present", "absent"], "default": "present"},
                },
                "required": True,
            },
            "concurrency": {"type": "int", "default": 10},
        },
    ) as module:
        module.process_batch(module.params["repositories"], module.params["concurrency"])


if __name__ == "__main__":
    main()

