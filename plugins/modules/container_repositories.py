#!/usr/bin/python

# copyright (c) 2021, Mark Goddard
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
extends_documentation_fragment:
  - pulp.squeezer.pulp
author:
  - Mark Goddard (@markgoddard)
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

from ansible_collections.pulp.squeezer.plugins.module_utils.pulp_glue import PulpAnsibleModule

try:
    from pulp_glue.container.context import PulpContainerRepositoryContext

    PULP_GLUE_IMPORT_ERR = None
except ImportError:
    PULP_GLUE_IMPORT_ERR = traceback.format_exc()
    PulpContainerRepositoryContext = None


class PulpBatchEntityAnsibleModule(PulpAnsibleModule):
    def __init__(self, context_class, **kwargs):
        super().__init__(**kwargs)
        self.context_class = context_class

    def process_batch(self, entities):
        results = []
        overall_changed = False
        for entity in entities:
            result = {
                "name": entity["name"],
                "changed": False,
                "failed": False,
                "msg": "",
            }
            try:
                context = self.context_class(self.pulp_ctx)
                natural_key = {"name": entity["name"]}
                desired_attributes = {}
                if "description" in entity and entity["description"] is not None:
                    desired_attributes["description"] = entity["description"]

                state = entity.get("state", "present")
                if state == "present":
                    desired_entity = desired_attributes
                elif state == "absent":
                    desired_entity = None
                else:
                    result["failed"] = True
                    result["msg"] = f"Invalid state '{state}'"
                    results.append(result)
                    continue

                # Simulate the converge logic
                context.entity = natural_key
                changed, before, after = context.converge(desired_entity)
                if changed:
                    result["changed"] = True
                    overall_changed = True
                if after is not None:
                    result["repository"] = after
            except Exception as e:
                result["failed"] = True
                result["msg"] = str(e)
            results.append(result)

        if overall_changed:
            self.set_changed()
        self.set_result("repositories", results)


def main():
    with PulpBatchEntityAnsibleModule(
        context_class=PulpContainerRepositoryContext,
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
        },
    ) as module:
        module.process_batch(module.params["repositories"])


if __name__ == "__main__":
    main()
