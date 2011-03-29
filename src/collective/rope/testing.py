from plone.testing import z2

from plone.bbb_testing import cmf_layers

import plone.app.testing.layers

import collective.rope


SIMPLE_ITEM_MAPPER = 'collective.rope.tests.simpleitem.RopeSimpleItem'
PORTAL_CONTENT_MAPPER = 'collective.rope.tests.portalcontent.RopePortalContent'
AT_CONTENT_MAPPER = 'collective.rope.tests.atcontent.RopeATContent'

ROPE_FIXTURE = plone.testing.zca.ZCMLSandbox(bases=(z2.STARTUP,),
    name="ROPE_FIXTURE",
    filename="testingzope.zcml", package=collective.rope)


class RopeInstall(plone.testing.Layer):

    defaultBases = (ROPE_FIXTURE,)

    def setUp(self):
        with z2.zopeApp() as app:
            z2.installProduct(app, 'collective.rope')

    def tearDown(self):
        with z2.zopeApp() as app:
            z2.uninstallProduct(app, 'collective.rope')

ROPE_INSTALL = RopeInstall(name="ROPE_INSTALL")

ROPE_INTEGRATION = z2.IntegrationTesting(bases=(ROPE_FIXTURE,),
    name="ROPE_INTEGRATION")

ROPE_FUNCTIONAL = z2.FunctionalTesting(
    bases=(ROPE_INSTALL, ),
    name="ROPE_FUNCTIONAL")

CMF_ROPE_ZCML_FIXTURE = plone.testing.zca.ZCMLSandbox(
    bases=(ROPE_FIXTURE, ),
    name="CMF_ROPE_ZCML_FIXTURE",
    filename="testingcmf.zcml", package=collective.rope)


class CMFRope(plone.testing.Layer):
    # Rope ZCML must be setup before CMF portal local registry is hooked to a
    # global registry
    defaultBases = (CMF_ROPE_ZCML_FIXTURE, cmf_layers.PORTAL_FIXTURE)

    def setUp(self):
        with cmf_layers.CMFDefaultPortal() as portal:
            cmf_layers.applyProfile(portal,
                'collective.rope.tests:ropeoncmf')

CMF_ROPE_FIXTURE = CMFRope(name="CMF_ROPE_FIXTURE")

CMF_ROPE_INTEGRATION = cmf_layers.IntegrationTesting(
    bases=(CMF_ROPE_FIXTURE, ),
    name='CMF_ROPE_INTEGRATION')

CMF_ROPE_FUNCTIONAL = cmf_layers.FunctionalTesting(
    bases=(CMF_ROPE_FIXTURE, ),
    name='CMF_ROPE_FUNCTIONAL')

PLONE_ROPE_FIXTURE = plone.app.testing.PloneWithPackageLayer(
    name="PLONE_ROPE_FIXTURE",
    zcml_filename="testingplone.zcml",
    zcml_package=collective.rope,
    gs_profile_id='collective.rope.tests:ropeonat'
    )

PLONE_ROPE_INTEGRATION = plone.app.testing.layers.IntegrationTesting(
    bases=(PLONE_ROPE_FIXTURE, ),
    name='PTC_PLONE_ROPE_INTEGRATION')

PLONE_ROPE_FUNCTIONAL = plone.app.testing.layers.FunctionalTesting(
    bases=(PLONE_ROPE_FIXTURE, ),
    name='PTC_PLONE_ROPE_FUNCTIONAL')
