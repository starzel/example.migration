# -*- coding: utf-8 -*-
from plone import api
from plone.app.textfield.interfaces import TransformError
from plone.app.textfield.value import RichTextValue
from plone.app.theming.utils import applyTheme
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.PluginIndexes.common import safe_callable
from plone.app.layout.navigation.interfaces import INavigationRoot
from OFS.CopySupport import CopyError
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zExceptions import BadRequest

import logging
import transaction

log = logging.getLogger(__name__)


def cleanup_addons(setup):
    """1000 -> 1001
    Step is to be run in Plone 4.3.x
    """
    patch_indexing_at_blobs()
    patch_indexing_dx_blobs()

    # init
    portal = api.portal.get()
    catalog = api.portal.get_tool('portal_catalog')
    qi = api.portal.get_tool('portal_quickinstaller')
    css = api.portal.get_tool('portal_css')
    controlpanel = api.portal.get_tool('portal_controlpanel')
    portal_properties = api.portal.get_tool('portal_properties')
    portal_skins = api.portal.get_tool('portal_skins')

    to_delete = [
        '/nm/microsite/sip/astrid/carousel',
        '/nm/nuetzliches/carousel',
    ]
    for path in to_delete:
        try:
            obj = api.content.get(path=path)
            if obj is not None:
                api.content.delete(obj, check_linkintegrity=False)
        except:
            continue
        log.info('Deleted %s' % path)

    # remove overrides
    custom = portal_skins['custom']
    for name in custom.keys():
        custom.manage_delObjects([name])

    log.info('removing portal_view_customizations')
    view_customizations = api.portal.get_tool('portal_view_customizations')
    for name in view_customizations.keys():
        view_customizations.manage_delObjects([name])

    # Remove collective.easyslider
    if qi.isProductInstalled('collective.easyslider'):
        from collective.easyslider.interfaces import IViewEasySlider
        for brain in api.content.find(
                object_provides=IViewEasySlider.__identifier__):
            obj = brain.getObject()
            # noLongerProvides(obj, IViewEasySlider)
            if obj.getLayout() == 'sliderview':
                obj.manage_delProperties(['layout'])
                log.info('removed easyslider from {}'.format(brain.getURL()))
        controlpanel.unregisterConfiglet('easyslieder')
        qi.uninstallProducts(['collective.easyslider'])
    try:
        portal_properties.manage_delObjects(['easyslideshow_properties'])
    except BadRequest:
        pass

    # remove cciaa.modulistica
    log.info('removing cciaa.modulistica')
    if qi.isProductInstalled('cciaa.modulistica'):
        catalog._removeIndex('getRawRelatedItems')
        css.manage_removeStylesheet('++resource++cciaa.modulistica.stylesheets/cciaa.modulistica.css')  # noqa: E501
        from cciaa.modulistica.interfaces import CCIAAModAbleContent
        for brain in api.content.find(
                object_provides=CCIAAModAbleContent.__identifier__):
            obj = brain.getObject()
            # noLongerProvides(obj, IViewEasySlider)
            if obj.getLayout() == 'cciaa_modulistica_view':
                obj.manage_delProperties(['layout'])
                log.info('removed cciaa.modulistica from {}'.format(brain.getURL()))  # noqa: E501
        qi.uninstallProducts(['cciaa.modulistica'])

    # Solgema.fullcalendar
    log.info('removing Solgema.fullcalendar')
    if qi.isProductInstalled('Solgema.fullcalendar'):
        qi.uninstallProducts(['Solgema.fullcalendar'])

    # collective.imagetags
    log.info('removing collective.imagetags')
    if qi.isProductInstalled('collective.imagetags'):
        controlpanel.unregisterConfiglet('imagetags')
        # do not uninstall utilities since that will nuke the registry
        cascade = [
            'types', 'skins', 'actions', 'portalobjects', 'workflows', 'slots',
            'registrypredicates', 'adapters']
        qi.uninstallProducts(['collective.imagetags'], cascade=cascade)

    # wpd.mmxi.countdown
    # delete portlet instance
    log.info('removing wpd.mmxi.countdown')
    content = api.content.get(path='/nm/example-intranet')
    if content:
        manager = getUtility(
            IPortletManager, name='plone.leftcolumn', context=content)
        mapping = getMultiAdapter(
            (content, manager), IPortletAssignmentMapping)
        try:
            del mapping['wpd-countdown']
        except KeyError:
            pass

    if qi.isProductInstalled('wpd.mmxi.countdown'):
        qi.uninstallProducts(['wpd.mmxi.countdown'])
    try:
        setup.manage_deleteImportSteps(['wpd.mmxi.countdown-upgrades'])
    except KeyError:
        pass

    # Products.Carousel
    log.info('removing Products.Carousel')
    if qi.isProductInstalled('Products.Carousel'):
        qi.uninstallProducts(['Products.Carousel'])

    # Products.PlonePopoll
    log.info('removing Products.PlonePopoll')
    if qi.isProductInstalled('PlonePopoll'):
        qi.uninstallProducts(['PlonePopoll'])

    # eea.facetednavigation
    log.info('removing eea.facetednavigation')
    if qi.isProductInstalled('eea.facetednavigation'):
        qi.uninstallProducts(['eea.facetednavigation'])

    # eea.relations
    log.info('removing eea.relations')
    if qi.isProductInstalled('eea.relations'):
        qi.uninstallProducts(['eea.relations'])

    # Products.ECLecture
    log.info('removing Products.ECLecture')
    if qi.isProductInstalled('ECLecture'):
        qi.uninstallProducts(['ECLecture'])

    # Products.ImageEditor
    log.info('removing Products.ImageEditor')
    if qi.isProductInstalled('ImageEditor'):
        qi.uninstallProducts(['ImageEditor'])

    # collective.plonetruegallery
    log.info('removing collective.plonetruegallery')
    if qi.isProductInstalled('collective.plonetruegallery'):
        qi.uninstallProducts(['collective.plonetruegallery'])
    try:
        setup.manage_deleteImportSteps(['collective.plonetruegallery.install'])
    except KeyError:
        pass

    # zettwerk.ui
    log.info('removing zettwerk.ui')
    if qi.isProductInstalled('zettwerk.ui'):
        qi.uninstallProducts(['zettwerk.ui'])
    try:
        setup.manage_deleteImportSteps(['zettwerk.ui.disable_sunburst_patch'])
    except KeyError:
        pass

    # Solgema.fullcalendar
    log.info('removing Solgema.fullcalendar')
    if qi.isProductInstalled('Solgema.fullcalendar'):
        qi.uninstallProducts(['Solgema.fullcalendar'])

    # Solgema.ContextualContentMenu
    log.info('removing Solgema.ContextualContentMenu')
    if qi.isProductInstalled('Solgema.ContextualContentMenu'):
        qi.uninstallProducts(['Solgema.ContextualContentMenu'])

    # Products.ImageEditor
    log.info('removing Products.ImageEditor')
    if qi.isProductInstalled('Products.ImageEditor'):
        qi.uninstallProducts(['Products.ImageEditor'])
    try:
        portal_properties.manage_delObjects(['imageeditor'])
    except BadRequest:
        pass

    # collective.easyslideshow
    log.info('removing collective.easyslideshow')
    if qi.isProductInstalled('collective.easyslideshow'):
        qi.uninstallProducts(['collective.easyslideshow'])
    try:
        portal_properties.manage_delObjects(['easyslideshow_properties'])
    except BadRequest:
        pass

    # this is tough magic. It us called multiple times because it does not hurt
    # same things die hard
    _unregisterUtility(portal)

    # collective.quickupload
    log.info('removing collective.quickupload')
    if qi.isProductInstalled('collective.quickupload'):
        qi.uninstallProducts(['collective.quickupload'])
    try:
        portal_properties.manage_delObjects(['quickupload_properties'])
    except BadRequest:
        pass

    # collective.prettyphoto
    log.info('removing collective.prettyphoto')
    if qi.isProductInstalled('collective.prettyphoto'):
        qi.uninstallProducts(['collective.prettyphoto'])
    try:
        portal_properties.manage_delObjects(['prettyphoto_properties'])
    except BadRequest:
        pass

    # collective.plonefinder
    log.info('removing collective.plonefinder')
    if qi.isProductInstalled('collective.plonefinder'):
        qi.uninstallProducts(['collective.plonefinder'])

    # Products.PloneFormGen
    log.info('removing Products.PloneFormGen')
    if qi.isProductInstalled('PloneFormGen'):
        qi.uninstallProducts(['PloneFormGen'])
    try:
        portal_properties.manage_delObjects(['ploneformgen_properties'])
    except BadRequest:
        pass

    # DataGridField
    log.info('removing DataGridField')
    if qi.isProductInstalled('DataGridField'):
        qi.uninstallProducts(['DataGridField'])

    # collective.js.fullcalendar
    log.info('removing collective.js.fullcalendar')
    if qi.isProductInstalled('collective.js.fullcalendar'):
        qi.uninstallProducts(['collective.js.fullcalendar'])

    # Products.PloneFlashUpload (not installed)
    log.info('removing Products.PloneFlashUpload')
    if qi.isProductInstalled('Products.PloneFlashUpload'):
        qi.uninstallProducts(['Products.PloneFlashUpload'])

    # p4a.subtyper
    log.info('removing p4a.subtyper')
    if qi.isProductInstalled('p4a.subtyper'):
        qi.uninstallProducts(['p4a.subtyper'])

    # collective.externaleditor
    log.info('removing collective.externaleditor')
    if qi.isProductInstalled('collective.externaleditor'):
        qi.uninstallProducts(['collective.externaleditor'])

    # collective.ckeditor
    log.info('removing collective.ckeditor')
    if qi.isProductInstalled('collective.ckeditor'):
        qi.uninstallProducts(['collective.ckeditor'])
    try:
        portal_properties.manage_delObjects(['ckeditor_properties'])
    except BadRequest:
        pass

    # redturtle.smartlink
    log.info('removing redturtle.smartlink')
    if qi.isProductInstalled('redturtle.smartlink'):
        # run migration
        setup.runAllImportStepsFromProfile(
            'profile-redturtle.smartlink:smartLinkToATLink', purge_old=False)
        qi.uninstallProducts(['redturtle.smartlink'])

    # collective.js.jqueryui
    log.info('removing collective.js.jqueryui')
    if qi.isProductInstalled('collective.js.jqueryui'):
        qi.uninstallProducts(['collective.js.jqueryui'])
    try:
        portal_properties.manage_delObjects(['jqueryui_properties'])
    except BadRequest:
        pass

    # finally run uninstall-profile
    log.info('run step to_1001')
    setup.runAllImportStepsFromProfile(
        'profile-example.migration:to_1001', purge_old=False)

    # other
    log.info('remove configlets')
    controlpanel.unregisterConfiglet('UsersGroups2')
    controlpanel.unregisterConfiglet('clickmap')
    # controlpanel.unregisterConfiglet('WindowZTool')
    controlpanel.unregisterConfiglet('EasySlideshowConfiguration')
    # controlpanel.unregisterConfiglet('portal_atct')
    controlpanel.unregisterConfiglet('PloneFormGen')
    controlpanel.unregisterConfiglet('SmartlinkConfig')
    controlpanel.unregisterConfiglet('QuickUpload')
    controlpanel.unregisterConfiglet('CKEditor')

    broken_import_steps = [
        u'ECLecture-GS-dependencies',
        u'ECLecture-QI-dependencies',
        u'ECLecture-Update-RoleMappings',
        u'ECLecture-postInstall',
        u'Products.ImageEditor.install',
        u'Products.ImageEditor.uninstall',
        u'ckeditor-uninstall',
        u'collective.easyslider.install',
        u'collective.easyslider.uninstall',
        u'collective.prettyphoto.reset-layers',
        u'pleonformgen',
        u'solgemacontextualcontentmenu',
        u'solgemafullcalendarinstall',
        u'solgemafullcalendaruninstall',
    ]
    broken_export_steps = [u'possible_relations']

    log.info('remove import-steps')
    registry = setup.getImportStepRegistry()
    for broken_import_step in broken_import_steps:
        if broken_import_step in registry.listSteps():
            registry.unregisterStep(broken_import_step)

    log.info('remove export-steps')
    registry = setup.getExportStepRegistry()
    for broken_export_step in broken_export_steps:
        if broken_export_step in registry.listSteps():
            registry.unregisterStep(broken_export_step)
    setup._p_changed = True

    # remove all instances of these types
    to_remove = [
        'FormFolder',
        'PlonePopoll',
        'ECLecture',
        'Person Folder',
        'Person',
    ]
    for brain in catalog(portal_type=to_remove, Language='all'):
        obj = brain.getObject()
        log.info('Deleting {} at {}'.format(
            to_remove, obj.absolute_url_path()))
        api.content.delete(obj, check_linkintegrity=False)

    # disable diazo theme 'example.theme' and enable default sunburst
    log.info('remove example.theme')
    if qi.isProductInstalled('example.theme'):
        qi.uninstallProducts(['example.theme'])
    applyTheme(None)
    portal_skins.default_skin = 'Sunburst Theme'
    if 'example Theme' in portal_skins.getSkinSelections():
        portal_skins.manage_skinLayers(['example Theme'], del_skin=True)

    # delete unused carousel folders (folders with images)
    for brain in catalog(object_provides='Products.Carousel.interfaces.ICarouselFolder', Language='all'):  # noqa: E501
        obj = brain.getObject()
        log.info('Deleting {} at {}'.format(
            obj.portal_type, obj.absolute_url_path()))
        api.content.delete(obj, check_linkintegrity=False)

    # delete no longer used objects that use eea.facetednavigation
    for brain in catalog(object_provides='eea.facetednavigation.settings.interfaces.IDisableSmartFacets', Language='all'):  # noqa: E501
        obj = brain.getObject()
        log.info('Deleting {} at {}'.format(
            obj.portal_type, obj.absolute_url_path()))
        api.content.delete(obj, check_linkintegrity=False)

    log.info('rebuilding catalog')
    catalog.clearFindAndRebuild()

    # reset viewlet-order
    log.info('order viewlets')
    setup.runImportStepFromProfile(
        'profile-Products.CMFPlone:plone',
        step_id='viewlets',
        run_dependencies=False)
    unregister_broken_persistent_components(portal)
    unpatch_indexing_at_blobs()
    unpatch_indexing_dx_blobs()


def _unregisterUtility(portal):
    from p4a.subtyper.interfaces import IPortalTypedFolderishDescriptor
    sm = portal.getSiteManager()
    util = sm.queryUtility(
        IPortalTypedFolderishDescriptor, u'collective.easyslideshow.slideshow')
    sm.unregisterUtility(
        util,
        IPortalTypedFolderishDescriptor,
        name=u'collective.easyslideshow.slideshow')
    if IPortalTypedFolderishDescriptor in sm.utilities._subscribers[0]:
        del sm.utilities._subscribers[0][IPortalTypedFolderishDescriptor]
    from collective.lineage.upgrades import removeP4A
    removeP4A(portal)
    remove_vocabularies(None)


def cleanup_content_for_pam(setup):
    """Set languages, add and link translations so that we can migrate to pam
    Run this Plone 4.3.x
    """
    patch_indexing_at_blobs()
    patch_indexing_dx_blobs()

    portal = api.portal.get()
    unregister_broken_persistent_components(portal)

    # set language of containers without lang to a sane value
    for brain in api.content.find(
            portal_type=['Folder', 'Section'], Language=''):
        obj = brain.getObject()
        content = obj.contentValues()
        lang = set([i.Language() for i in content])
        if lang and len(lang) == 1:
            lang = lang.pop()
            if not lang:
                lang = 'de'
        else:
            lang = 'de'
        obj.setLanguage(lang)
        log.info('Set language of %s to %s' % (obj.absolute_url_path(), lang))
        obj.reindexObject(idxs=['Language'])
    transaction.commit()

    # add missing translations for parents of english content
    brains = [i for i in api.content.find(Language='en')]
    done = []
    for brain in brains:
        try:
            if brain.getPath() in done:
                continue
            obj = brain.getObject()
        except KeyError:
            continue
        if IPloneSiteRoot.providedBy(obj) or INavigationRoot.providedBy(obj):
            continue
        parent = obj.__parent__
        if IPloneSiteRoot.providedBy(parent):
            continue

        if parent.Language() == 'en':
            continue

        if parent.hasTranslation('en'):
            translation = parent.getTranslation('en')
            if translation.absolute_url_path() != parent.absolute_url_path():
                log.info('Parent container has a translation. Moving %s to %s' % (obj.absolute_url_path(), translation.absolute_url_path()))  # noqa: E501
                api.content.move(source=obj, target=translation, safe_id=True)
            continue

        content = parent.contentValues()
        if content and 'de' not in [i.Language() for i in content]:
            parent.setLanguage('en')
            log.info('Switched container with english-only content to english. Please link translation of %s!' % parent.absolute_url_path())  # noqa: E501
            obj.reindexObject(idxs=['Language'])
            for child_obj in content:
                if child_obj.Language() != 'en':
                    child_obj.setLanguage('en')
                    child_obj.reindexObject(idxs=['Language'])
            continue

        if not parent.Language():
            log.error('Crap! Container without lang: %s' % parent.absolute_url_path())  # noqa: E501
            continue

        if parent.getId().endswith('-en'):
            log.error('Crap! Weird things at: %s' % parent.absolute_url_path())
            continue

        try:
            translation = parent.addTranslation('en')
        except CopyError:
            log.info('Could not create english translation of %s' % parent.absolute_url_path())  # noqa: E501
            pass
        done.append('/'.join(parent.getPhysicalPath()))
        log.info('Add translation of %s: %s' % (
            parent.absolute_url_path(), translation))
    transaction.commit()

    brains = [i for i in api.content.find(Language='de')]
    done = []
    for brain in brains:
        try:
            if brain.getPath() in done:
                continue
            obj = brain.getObject()
        except KeyError:
            continue
        if IPloneSiteRoot.providedBy(obj) or INavigationRoot.providedBy(obj):
            continue
        parent = obj.__parent__
        if IPloneSiteRoot.providedBy(parent):
            continue
        if parent.Language() == 'de':
            continue

        if parent.hasTranslation('de'):
            log.error('Crap! Weird things at: %s' % parent.absolute_url_path())
            continue

        if not parent.Language():
            parent.setLanguage('de')
            log.info('Switched container to german: %s!' % parent.absolute_url_path())  # noqa: E501
            obj.reindexObject(idxs=['Language'])
            continue

        content = parent.contentValues()
        if 'en' not in [i.Language() for i in content]:
            parent.setLanguage('de')
            log.info('Switched container to german: %s!' % parent.absolute_url_path())  # noqa: E501
            obj.reindexObject(idxs=['Language'])
            for child_obj in content:
                if child_obj.Language() != 'de':
                    child_obj.setLanguage('de')
                    child_obj.reindexObject(idxs=['Language'])
            continue

        if parent.getId().endswith('-en'):
            log.error('Crap! Weird things at: %s' % parent.absolute_url_path())

    # set language of all neutral content to 'de'
    transaction.commit()
    for brain in api.content.find(Language=''):
        obj = brain.getObject()
        if not obj.Language():
            if not obj.isCanonical() and 'de' in obj.getTranslations():
                lang = 'en'
            else:
                lang = 'de'
            obj.setLanguage(lang)
            obj.reindexObject(idxs=['Language'])
            log.info('Switched %s to %s' % (obj.absolute_url_path(), lang))

    # log non-default content with different languages than their parents
    find_content_with_wrong_language(portal)
    unpatch_indexing_at_blobs()
    unpatch_indexing_dx_blobs()


def install_pam(setup):
    """Run this Plone 4.3.x

    Install pam - we still use Archetyoes, so also archetypes.multilingual
    """
    qi = api.portal.get_tool('portal_quickinstaller')
    portal = api.portal.get()

    if not qi.isProductInstalled('plone.app.multilingual'):
        qi.installProduct('plone.app.multilingual')
        qi.installProduct('archetypes.multilingual')
        from plone.app.multilingual.browser.setup import SetupMultilingualSite
        ml_setup_tool = SetupMultilingualSite()
        ml_setup_tool.setupSite(portal)


def migrate_to_pam(setup):
    """Run this Plone 4.3.x

    Install LinguaPlone to plone.app.multilingual
    This uses the migration that is builtin in pam
    """

    patch_indexing_at_blobs()
    patch_indexing_dx_blobs()

    qi = api.portal.get_tool('portal_quickinstaller')
    portal_properties = api.portal.get_tool('portal_properties')
    portal = api.portal.get()

    # again set the language of containers without lang to a sane value
    # This information gets lost somehow
    for brain in api.content.find(
            portal_type=['Folder', 'Section'], Language=''):
        obj = brain.getObject()
        content = obj.contentValues()
        lang = set([i.Language() for i in content])
        if lang and len(lang) == 1:
            lang = lang.pop()
            if not lang:
                lang = 'de'
        else:
            lang = 'de'
        obj.setLanguage(lang)
        log.info('Set language of %s to %s' % (obj.absolute_url_path(), lang))
        obj.reindexObject(idxs=['Language'])

    # run all lp migration-steps
    from zope.globalrequest import getRequest
    request = getRequest()
    lp_relocate = api.content.get_view('relocate-content', portal, request)
    lp_relocate.blacklist = []
    lp_relocate.step1andstep2()
    transaction.commit()
    lp_relocate.step3()
    transaction.commit()
    transfer_lp_catalog = api.content.get_view(
        'transfer-lp-catalog', portal, request)
    transfer_lp_catalog()
    transaction.commit()

    # remove LinguaPlone
    if qi.isProductInstalled('LinguaPlone'):
        qi.uninstallProducts(['LinguaPlone'])
    try:
        portal_properties.manage_delObjects(['linguaplone_properties'])
    except BadRequest:
        pass
    # run our LP-uninstall-profile
    setup.runAllImportStepsFromProfile(
        'profile-example.migration:to_1005', purge_old=False)
    unpatch_indexing_at_blobs()
    unpatch_indexing_dx_blobs()


def remove_vocabularies(setup):
    from plone.i18n.locales.interfaces import IContentLanguageAvailability
    from plone.i18n.locales.interfaces import IMetadataLanguageAvailability
    from p4a.subtyper.interfaces import IPortalTypedFolderishDescriptor
    portal = api.portal.get()
    sm = portal.getSiteManager()

    if IContentLanguageAvailability in sm.utilities._subscribers[0]:
        del sm.utilities._subscribers[0][IContentLanguageAvailability]
        log.info(u'Unregistering subscriber for IContentLanguageAvailability')
    if IMetadataLanguageAvailability in sm.utilities._subscribers[0]:
        del sm.utilities._subscribers[0][IMetadataLanguageAvailability]
        log.info(u'Unregistering subscriber for IMetadataLanguageAvailability')

    if IMetadataLanguageAvailability in sm.utilities._adapters[0]:
        del sm.utilities._adapters[0][IMetadataLanguageAvailability]
        log.info(u'Unregistering adapter for IMetadataLanguageAvailability')
    if IContentLanguageAvailability in sm.utilities._adapters[0]:
        del sm.utilities._adapters[0][IContentLanguageAvailability]
        log.info(u'Unregistering adapter for IContentLanguageAvailability')

    if IPortalTypedFolderishDescriptor in sm.utilities._adapters[0]:
        del sm.utilities._adapters[0][IPortalTypedFolderishDescriptor]
        log.info(u'Unregistering adapter for IPortalTypedFolderishDescriptor')
    sm.utilities._p_changed = True
    transaction.commit()


def unregister_broken_persistent_components(portal):
    sm = portal.getSiteManager()

    for item in sm._utility_registrations.items():
        if hasattr(item[1][0], '__Broken_state__'):
            # unregisterUtility(component, provided, name)
            # See: five.localsitemanager.registry.PersistentComponents.unregisterUtility  # noqa: E501
            log.info(u"Unregistering component {0}".format(item))
            sm.unregisterUtility(item[1][0], item[0][0], item[0][1])


def find_content_with_wrong_language(content):
    """log non-default content with different languages than their parents
    Used to make sure we cleaned up everything.

    In part stolen and adapted from
    plone.app.multilingual.browser.migrator.moveContentToProperRLF.findContent
    """
    # only handle portal content
    from plone.dexterity.interfaces import IDexterityContent
    from Products.Archetypes.interfaces import IBaseObject
    from Acquisition import aq_base
    from Acquisition import aq_parent
    try:
        from Products.LinguaPlone.interfaces import ITranslatable
    except ImportError:
        from plone.app.multilingual.interfaces import ITranslatable

    if not IDexterityContent.providedBy(content)\
            and not IBaseObject.providedBy(content)\
            and not IPloneSiteRoot.providedBy(content):
        return
    if hasattr(aq_base(content), 'objectIds'):
        for id in content.objectIds():
            find_content_with_wrong_language(getattr(content, id))
    if ITranslatable.providedBy(content):
        # The content parent has the same language?
        if not IPloneSiteRoot.providedBy(aq_parent(content)) \
           and aq_parent(content).Language() != content.Language():
            log.info('Obj %s (%s) not same language as parent (%s)' % (
                content.absolute_url_path(), content.Language(), aq_parent(content).Language()))  # noqa: E501


def cleanup_after_pam_migration(setup):
    """Nothing yet"""
    return


def prepare_p5_upgrade(setup):
    """Run this in Plone 5.x before running the upgrade from Plone 4 to 5!!!
    """
    broken_import_steps = [
        u'collective.z3cform.datetimewidget',
        u'languagetool',
        u'smartLinkToATLink',
    ]
    registry = setup.getImportStepRegistry()
    for broken_import_step in broken_import_steps:
        if broken_import_step in registry.listSteps():
            registry.unregisterStep(broken_import_step)

    # reinstall plone.app.iterate
    qi = api.portal.get_tool('portal_quickinstaller')
    qi.reinstallProducts(['plone.app.iterate'])
    setup.runAllImportStepsFromProfile(
        'profile-plone.app.z3cform:default', purge_old=False)


def after_p5_upgrade(setup):
    """Run this in Plone 5.x after the upgrade from Plone 4 to 5!!!
    """
    qi = api.portal.get_tool('portal_quickinstaller')

    # reinstall some addons
    qi.reinstallProducts(['CMFPlacefulWorkflow'])
    qi.reinstallProducts(['webcouturier.dropdownmenu'])
    qi.reinstallProducts(['plone.app.ldap'])
    qi.reinstallProducts(['Reflecto'])

    # install pac
    qi.installProduct('plone.app.contenttypes')

    # reinstall pam
    qi.reinstallProducts(['plone.app.multilingual'])
    qi.reinstallProducts(['archetypes.multilingual'])

    # install theme
    qi.installProducts(['example.theme'])

    # from plone.app.multilingual import setuphandlers
    # setuphandlers.enable_translatable_behavior(api.portal.get())


def migrate_folders(setup):
    """Run this in Plone 5.x
    """
    patch_indexing_at_blobs()
    patch_indexing_dx_blobs()

    portal = api.portal.get()
    request = getRequest()

    pac_migration = api.content.get_view('migrate_from_atct', portal, request)
    content_types = ['Folder']

    pac_migration(
        migrate=True,
        content_types=content_types,
        migrate_schemaextended_content=True,
        reindex_catalog=True)

    unpatch_indexing_at_blobs()
    unpatch_indexing_dx_blobs()


def migrate_to_pac(setup):
    """Run this in Plone 5.x
    """
    patch_indexing_at_blobs()
    patch_indexing_dx_blobs()

    portal = api.portal.get()
    request = getRequest()

    pac_migration = api.content.get_view('migrate_from_atct', portal, request)
    content_types = ['News Item', 'Document', 'Image', 'Collection', 'BlobImage', 'Event']  # noqa: E501

    pac_migration(
        migrate=True,
        content_types=content_types,
        migrate_schemaextended_content=True,
        reindex_catalog=True)

    unpatch_indexing_at_blobs()
    unpatch_indexing_dx_blobs()


def migrate_topics(setup):
    """Run this in Plone 5.x
    """
    patch_indexing_at_blobs()
    patch_indexing_dx_blobs()

    portal = api.portal.get()
    request = getRequest()
    pac_migration = api.content.get_view('migrate_from_atct', portal, request)
    content_types = ['Topic']
    pac_migration(
        migrate=True,
        content_types=content_types,
        migrate_schemaextended_content=True,
        reindex_catalog=True)

    unpatch_indexing_at_blobs()
    unpatch_indexing_dx_blobs()


def migrate_files(setup):
    """Run this in Plone 5.x
    """
    patch_indexing_at_blobs()
    patch_indexing_dx_blobs()

    portal = api.portal.get()
    request = getRequest()

    pac_migration = api.content.get_view('migrate_from_atct', portal, request)
    content_types = ['BlobFile', 'File']

    pac_migration(
        migrate=True,
        content_types=content_types,
        migrate_schemaextended_content=True,
        reindex_catalog=True)

    unpatch_indexing_at_blobs()
    unpatch_indexing_dx_blobs()


def migrate_links(setup):
    """Run this in Plone 5.x
    """
    patch_indexing_at_blobs()
    patch_indexing_dx_blobs()

    portal = api.portal.get()
    request = getRequest()
    pac_migration = api.content.get_view('migrate_from_atct', portal, request)
    content_types = ['Link']
    pac_migration(
        migrate=True,
        content_types=content_types,
        migrate_schemaextended_content=True,
        reindex_catalog=False)

    unpatch_indexing_at_blobs()
    unpatch_indexing_dx_blobs()


def cleanup_after_pac_migration(setup):
    """Run this in Plone 5.x
    """
    patch_indexing_at_blobs()
    patch_indexing_dx_blobs()

    log.info('Rebuilding catalog...')
    portal_catalog = api.portal.get_tool('portal_catalog')
    portal_catalog.clearFindAndRebuild()
    log.info('Done!')
    log.info('Set startpageview')
    portal = api.portal.get()
    portal['de'].setLayout('startpageview')
    portal['en'].setLayout('startpageview')
    for brain in api.content.find(portal_type=['Folder', 'Collection']):
        obj = brain.getObject()
        if obj.getLayout() == 'prettyPhoto_album_view':
            obj.setLayout('album_view')
            log.info('Removed prettyPhoto from %s' % obj.absolute_url_path())
    portal_transforms = api.portal.get_tool('portal_transforms')
    portal_transforms.reloadTransforms(['safe_html'])
    log.info('Reloaded safe_html transform!')
    # reinstall some steps from default profile
    setup.runAllImportStepsFromProfile(
        'profile-example.migration:default', purge_old=False)

    unpatch_indexing_at_blobs()
    unpatch_indexing_dx_blobs()


def rebuild_catalog_without_patch(setup):
    log.info('Rebuilding catalog...')
    portal_catalog = api.portal.get_tool('portal_catalog')
    portal_catalog.clearFindAndRebuild()
    log.info('Done!')


# Old scale name to new scale name
IMAGE_SCALE_MAP = {
    'icon': 'icon',
    'large': 'large',
    'listing': 'listing',
    'mini': 'mini',
    'preview': 'preview',
    'thumb': 'thumb',
    'tile': 'tile',
    # BBB
    'article': 'preview',
    'artikel': 'preview',
    'carousel': 'preview',
    'company_index': 'thumb',
    'content': 'preview',
    'leadimage': 'tile',
    'portlet-fullpage': 'large',
    'portlet-halfpage': 'large',
    'portlet-links': 'thumb',
    'portlet': 'thumb',
    'staff_crop': 'thumb',
    'staff_index': 'thumb',
}


def image_scale_fixer(text):
    if text:
        for old, new in IMAGE_SCALE_MAP.items():
            # replace plone.app.imaging old scale names with new ones
            text = text.replace(
                '@@images/image/{0}'.format(old),
                '@@images/image/{0}'.format(new)
            )
            # replace AT traversing scales
            text = text.replace(
                '/image_{0}'.format(old),
                '/@@images/image/{0}'.format(new)
            )
    return text


def fix_at_image_scales(setup):
    """Run this in Plone 5.x
    """
    catalog = api.portal.get_tool('portal_catalog')
    query = {}
    query['object_provides'] = 'plone.app.contenttypes.behaviors.richtext.IRichText'  # noqa
    results = catalog(**query)
    log.info('There are {0} in total, stating migration...'.format(
        len(results)))
    for result in results:
        try:
            obj = result.getObject()
        except:
            log.warning(
                'Not possible to fetch object from catalog result for '
                'item: {0}.'.format(result.getPath()))
            continue

        text = getattr(obj, 'text', None)
        if text:
            clean_text = image_scale_fixer(text.raw)
            if clean_text != text.raw:
                obj.text = RichTextValue(
                    raw=clean_text,
                    mimeType=text.mimeType,
                    outputMimeType=text.outputMimeType,
                    encoding=text.encoding
                )
                obj.reindexObject(idxs=('SearchableText', ))
                log.info('Text cleanup for {0}'.format(
                    '/'.join(obj.getPhysicalPath())
                ))


def pass_fn(*args, **kwargs):
    """Empty function used for patching."""
    pass


def upgrade_contenttype_section(setup):
    displayed_types = api.portal.get_registry_record('plone.displayed_types')
    displayed_types += ('Section', )
    api.portal.set_registry_record('plone.displayed_types', displayed_types)


def patch_indexing_at_blobs():
    from plone.app.blob.content import ATBlob
    from Products.contentmigration.utils import patch
    patch(ATBlob, 'getIndexValue', pass_fn)


def unpatch_indexing_at_blobs():
    from Products.contentmigration.utils import undoPatch
    from plone.app.blob.content import ATBlob
    undoPatch(ATBlob, 'getIndexValue')


def patch_indexing_dx_blobs():
    from Products.contentmigration.utils import patch
    from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex
    # from plone.app.blob.content import ATBlob
    patch(ZCTextIndex, 'index_object', patched_index_object)


def unpatch_indexing_dx_blobs():
    from Products.contentmigration.utils import undoPatch
    from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex
    undoPatch(ZCTextIndex, 'index_object')


def patched_index_object(self, documentId, obj, threshold=None):
    """Wrapper for  index_doc()  handling indexing of multiple attributes.

    Enter the document with the specified documentId in the index
    under the terms extracted from the indexed text attributes,
    each of which should yield either a string or a list of
    strings (Unicode or otherwise) to be passed to index_doc().
    """

    # patch: ignore Files
    if getattr(obj, 'portal_type', None) == 'File':
        return 0
    # TODO we currently ignore subtransaction threshold

    # needed for backward compatibility
    fields = getattr(self, '_indexed_attrs', [self._fieldname])

    all_texts = []
    for attr in fields:
        try:
            text = getattr(obj, attr, None)
        except TransformError as e:
            log.warn('TransformError accessing {0} of {1}: {2}'.format(attr, obj.absolute_url_path(), e))  # noqa: E501
            continue
        if text is None:
            continue
        if safe_callable(text):
            text = text()
        if text is not None:
            if isinstance(text, (list, tuple, set)):
                all_texts.extend(text)
            else:
                all_texts.append(text)

    # Check that we're sending only strings
    all_texts = [t for t in all_texts if isinstance(t, basestring)]
    if all_texts:
        return self.index.index_doc(documentId, all_texts)
    return 0


def fix_collections(setup):
    setup.runAllImportStepsFromProfile(
        'profile-example.migration:to_1051', purge_old=False)
