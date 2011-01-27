import zope.configuration

import plone.testing.z2
import plone.testing.zca

import collective.rope

from collective.rope.zopetestcasecompat import ZTCCompatIntegration
from collective.rope.zopetestcasecompat import ZTCCompatFunctional


class Rope(plone.testing.Layer):

    defaultBases = (plone.testing.z2.STARTUP, )

    def setUp(self):
        # Create a new global registry
        plone.testing.zca.pushGlobalRegistry()

        zope.configuration.xmlconfig.file(
            'testing.zcml', package=collective.rope,
            context=self['configurationContext'])
        with plone.testing.z2.zopeApp() as app:
            plone.testing.z2.installProduct(app, 'collective.rope')

    def tearDown(self):
        with plone.testing.z2.zopeApp() as app:
            plone.testing.z2.uninstallProduct(app, 'collective.rope')
        # Pop the global registry
        plone.testing.zca.popGlobalRegistry()


ROPE_FIXTURE = Rope(name="Rope")

ROPE_INTEGRATION = plone.testing.z2.IntegrationTesting(bases=(ROPE_FIXTURE,),
    name="Rope:Integration")

ROPE_FUNCTIONAL = plone.testing.z2.FunctionalTesting(bases=(ROPE_FIXTURE,),
name="Rope:Functional")

ZTC_ROPE_INTEGRATION = ZTCCompatIntegration(
    bases=(ROPE_FIXTURE, ),
    name='ZTC:Rope:Integration')

ZTC_ROPE_FUNCTIONAL = ZTCCompatFunctional(
    bases=(ROPE_FIXTURE, ),
    name='ZTC:Rope:Functional')
