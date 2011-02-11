import zope.configuration

import plone.testing.z2
import plone.testing.zca
import plone.app.testing.layers

import collective.rope

from collective.rope import cmf_layers

from collective.rope.zopetestcasecompat import ZTCCompatIntegration
from collective.rope.zopetestcasecompat import ZTCCompatFunctional


class RopeZcml(plone.testing.Layer):

    defaultBases = (plone.testing.z2.STARTUP, )

    def setUp(self):
        # Create a new global registry
        plone.testing.zca.pushGlobalRegistry()

        zope.configuration.xmlconfig.file(
            'testingzope.zcml', package=collective.rope,
            context=self.get('configurationContext'))
        with plone.testing.z2.zopeApp() as app:
            plone.testing.z2.installProduct(app, 'collective.rope')

    def tearDown(self):
        with plone.testing.z2.zopeApp() as app:
            plone.testing.z2.uninstallProduct(app, 'collective.rope')
        # Pop the global registry
        plone.testing.zca.popGlobalRegistry()


ROPE_FIXTURE = RopeZcml(name="RopeZcml")

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


class CMFRopeZcml(plone.testing.Layer):

    defaultBases = (ROPE_FIXTURE, )

    def setUp(self):
        # Create a new global registry
        plone.testing.zca.pushGlobalRegistry()
        zope.configuration.xmlconfig.file(
            'testingcmf.zcml', package=collective.rope,
            context=self.get('configurationContext'))

    def tearDown(self):
        # Pop the global registry
        plone.testing.zca.popGlobalRegistry()

CMF_ROPE_ZCML_FIXTURE = CMFRopeZcml(name="CMFRopeZcml")


class CMFRope(plone.testing.Layer):
    defaultBases = (CMF_ROPE_ZCML_FIXTURE, cmf_layers.PORTAL_FIXTURE)

    def setUp(self):
        with cmf_layers.CMFDefaultPortal() as portal:
            cmf_layers.applyProfile(portal,
                'collective.rope.tests:ropeoncmf')

CMF_ROPE_FIXTURE = CMFRope(name="CMFRope")

CMF_ROPE_INTEGRATION = cmf_layers.IntegrationTesting(
    bases=(CMF_ROPE_FIXTURE, ),
    name='CMFRope:Integration')

CMF_ROPE_FUNCTIONAL = cmf_layers.FunctionalTesting(
    bases=(CMF_ROPE_FIXTURE, ),
    name='CMFRope:Functional')


class PloneRopeZcml(plone.testing.Layer):

    defaultBases = (ROPE_FIXTURE, )

    def setUp(self):
        # Create a new global registry
        plone.testing.zca.pushGlobalRegistry()
        zope.configuration.xmlconfig.file(
            'testingplone.zcml', package=collective.rope,
            context=self.get('configurationContext'))

    def tearDown(self):
        # Pop the global registry
        plone.testing.zca.popGlobalRegistry()

PLONE_ROPE_ZCML_FIXTURE = PloneRopeZcml(name="PloneRopeZcml")


class PloneRope(plone.testing.Layer):
    defaultBases = (PLONE_ROPE_ZCML_FIXTURE, plone.app.testing.PLONE_FIXTURE)

    def setUp(self):
        from plone.app.testing import helpers

        with helpers.ploneSite() as portal:
            helpers.applyProfile(portal,
                'collective.rope.tests:ropeonat')

PLONE_ROPE_FIXTURE = PloneRope(name="PloneRope")

PTC_PLONE_ROPE_INTEGRATION = plone.app.testing.layers.IntegrationTesting(
    bases=(PLONE_ROPE_FIXTURE, ),
    name='PTC:PloneRope:Integration')

PTC_PLONE_ROPE_FUNCTIONAL = plone.app.testing.layers.FunctionalTesting(
    bases=(PLONE_ROPE_FIXTURE, ),
    name='PTC:PloneRope:Functional')
