# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

class ManifestEntity(object):
    resources = []

    def __init__(self):
        del self.resources[:]
        
    def add_resource(self, manifest_resource_entity):
        self.resources.append(manifest_resource_entity)


class ManifestResourceEntity(object):
    def __init__(self, identifier, resource_type, material_type, href, title = '', link_target = ''):
        self.identifier = identifier
        self.resource_type = resource_type
        self.material_type = material_type
        self.href = href
        self.title = title
        self.link_target = link_target