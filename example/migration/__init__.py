# -*- extra stuff goes here -*-
from example.migration import bbb
from plone.app.upgrade.utils import alias_module

# bbb classes
alias_module('collective.easyslideshow.descriptors.SlideshowDescriptor', bbb.SlideshowDescriptor)  # noqa: E501
alias_module('zettwerk.clickmap.ClickmapTool.ClickmapTool', bbb.SlideshowDescriptor)  # noqa: E501
alias_module('zettwerk.ui.tool.tool.UITool', bbb.UITool)
alias_module('p4a.subtyper.interfaces.IPortalTypedFolderishDescriptor', bbb.IBBB)  # noqa: E501
