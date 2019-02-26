Uninstall demo package
======================

This code is for reading and copy&paste when writing a in-place migration from Plone 4.x to 5.1.
Do not try to install or run it sincew that will not work unless you have the same set of requirements.

It was used in a real project where the old site used LinguaPlone (de and en).

Interesting things:

* upgrades.py: Hold all upgrade-steps
* upgrades.zcml: Registers the upgrade-steps and a couple of upgrade-profiles
* browser/views.py: more or less useful views to inspect the page before the migration
* __init__.py and bbb.py: aliases to keep running even if some stings could not be 100% uninstalled.

The following were the steps required to run the complete migration.

If you have questions or need help with a migration: Contact us at info@starzel.de


A. Prepare Database

- use branch master
- run ./bin/develop up -v
- run ./bin/buildout
- copy production-database
- Add a user: ./bin/instance adduser rescue rescue
- Startup: ./bin/instance fg
- Disable ldap connection:
  - http://localhost:8080/Plone/acl_users/ldap-plugin/manage_activateInterfacesForm -> uncheck all & save
- Rebuild catalog using view /Plone/@@rebuild_catalog_patched
- Run upgrade to Plone 4.3.15
- Pack Database


B. Remove Addons

- Run upgrade-step "Cleanup content and addons" of example.migration
- Run all remaining pending upgrade-steps except for those from example.migration (should be only one from collective.lineage)
- Run upgrade-step "Prepare migration to plone.app.multilingual" of example.migration
- AGAIN Run the upgrade-step "Prepare migration to plone.app.multilingual" of example.migration until no new translations are being created (three times)


C. Migrate from LinguaPlone to plone.app.multilingual
- Switch to branch 'migrate_to_pam' and run buildout
- Run ./bin/develop up -v
- Run ./bin/buildout
- start instance
- Run upgrade-step 'Install plone.app.multilingual and setup Site' of example.migration
- Run upgrade-step 'Migrate to plone.app.multilingual' of example.migration
- Run upgrade-step 'Remove vocabularies' of example.migration
- Run upgrade-step 'Cleanup after migration' of example.migration


E. Migrate to Plone 5.1

- Switch to branch 'plone5_migration',
- Run ./bin/develop up -v
- Run ./bin/buildout
- start instance
- Run upgrade-step "Prepare Plone 5 Migration" of example.migration
- Run Plone-Upgrade to 5.1rc1 (http://localhost:8080/Plone/@@plone-upgrade)
- Run upgrade-step "Finish Plone 5 Migration, prepare dexterity-migration" of example.migration
- One by one, run all upgrade-steps "Migrate xxx to Dexterity" of example.migration (~30 minutes without)
- Run upgrade-step "Cleanup after migrating to dexterity" of example.migration
- Run step "Fix image scales in links after migrating to dexterity" of example.migration
- Run upgrade-step "Upgrade content type Section" of example.migration
- Run remaining upgrade step:
  - Use registry instead of portal_windowz tool (Products.windowZ)
  - Re-run default profile to upgrade to 2.0 (collective.lineage)

F. Finish

- Switch to branch 'plone5'
- Run ./bin/develop up -v
- Run ./bin/buildout and start site
- Enable ldap connection:
  - http://localhost:8080/Plone/acl_users/ldap-plugin/manage_activateInterfacesForm -> check all & save
- Fix some viewlets manually: http://localhost:8080/Plone/de/manage-viewlets
  - show plone.app.multilingual.languageselector
  - order viewlets to be:
    - plone.logo
    - plone.anontools
    - plone.membertools
    - plone.app.multilingual.languageselector
    - plone.app.i18n.locales.languageselector (hidden)
    - plone.searchbox
    - collective.lineage.switcher

