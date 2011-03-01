from plone.testing import z2
from plone.testing import zca
import plone.app.testing.layers

import collective.rope

from collective.rope import cmf_layers

from collective.rope.zopetestcasecompat import ZTCCompatIntegration
from collective.rope.zopetestcasecompat import ZTCCompatFunctional


class RopeZcml(plone.testing.Layer):

    defaultBases = (z2.STARTUP, )

    def setUp(self):
        zca.setUpZcmlFiles((
            ('testingzope.zcml', collective.rope),
            ))
        with z2.zopeApp() as app:
            z2.installProduct(app, 'collective.rope')

    def tearDown(self):
        with z2.zopeApp() as app:
            z2.uninstallProduct(app, 'collective.rope')
        zca.tearDownZcmlFiles()


ROPE_FIXTURE = RopeZcml(name="RopeZcml")

ROPE_INTEGRATION = z2.IntegrationTesting(bases=(ROPE_FIXTURE,),
    name="Rope:Integration")

ROPE_FUNCTIONAL = z2.FunctionalTesting(bases=(ROPE_FIXTURE,),
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
        zca.setUpZcmlFiles((
            ('testingcmf.zcml', collective.rope),
            ))

    def tearDown(self):
        zca.tearDownZcmlFiles()


CMF_ROPE_ZCML_FIXTURE = CMFRopeZcml(name="CMFRopeZcml")


class CMFRope(plone.testing.Layer):
    # Rope ZCML must be setup before CMF portal local registry is hooked to a
    # global registry
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
        zca.setUpZcmlFiles((
            ('testingplone.zcml', collective.rope),
            ))

    def tearDown(self):
        zca.tearDownZcmlFiles()


PLONE_ROPE_ZCML_FIXTURE = PloneRopeZcml(name="PloneRopeZcml")


class PloneRope(plone.testing.Layer):
    # Rope ZCML must be setup before Plone portal local registry is hooked to a
    # global registry
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
