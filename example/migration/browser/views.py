# -*- coding: utf-8 -*-
from example.migration.upgrades import patch_indexing_at_blobs
from example.migration.upgrades import unpatch_indexing_at_blobs
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from zope.interface import alsoProvides

import logging
log = logging.getLogger(__name__)


class ExportLocalRoles(BrowserView):

    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        results_roles = {}
        results_block = [u'Items with disabled inheriting: ']
        for brain in catalog():
            obj = brain.getObject()
            local_roles = getattr(obj, '__ac_local_roles__', None)
            if local_roles:
                # drop owner
                for user, roles in local_roles.items():
                    if roles == ['Owner']:
                        local_roles.pop(user)
                if local_roles:
                    results_roles[obj.absolute_url_path()] = local_roles
            if getattr(obj, '__ac_local_roles_block__', None):
                results_block.append(obj.absolute_url_path())

        return [results_roles, results_block]


class RebuildCatalogPatched(BrowserView):

    def __call__(self):
        patch_indexing_at_blobs()
        alsoProvides(self.request, IDisableCSRFProtection)
        log.info('rebuilding catalog')
        catalog = api.portal.get_tool('portal_catalog')
        catalog.clearFindAndRebuild()
        unpatch_indexing_at_blobs()
        return 'Done'


class ExportContentStats(BrowserView):

    def __call__(self):
        pc = api.portal.get_tool('portal_catalog')
        self.results = []
        brains = pc.searchResults()
        for brain in brains:
            self.results.append('{0} ({1}): {2}'.format(
                brain.getPath(), brain.portal_type, brain.UID))
        log.info('total brains: {}'.format(len(brains)))
        return self.results
