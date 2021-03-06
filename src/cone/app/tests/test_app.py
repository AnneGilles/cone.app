import os
import doctest
import interlude
import pprint
import unittest2 as unittest
from zope.configuration.xmlconfig import XMLConfig
from plone.testing import layered
from cone.app import testing
import cone.app.tests

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE

layer = testing.security

TESTFILES = [
    '../__init__.rst',
    '../testing.rst',
    '../utils.rst',
    '../security.rst',
    '../model.rst',
    '../workflow.rst',
    '../browser/__init__.rst',
    '../browser/ajax.rst',
    '../browser/authoring.rst',
    '../browser/batch.rst',
    '../browser/table.rst',
    '../browser/contents.rst',
    '../browser/form.rst',
    '../browser/layout.rst',
    '../browser/login.rst',
    '../browser/workflow.rst',
    '../browser/referencebrowser.rst',
    '../browser/settings.rst',
    '../browser/utils.rst',
]

def test_suite():
    XMLConfig('dummy_workflow.zcml', cone.app.tests)()
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            doctest.DocFileSuite(
                testfile,
                globs={'interact': interlude.interact,
                       'pprint': pprint.pprint,
                       'pp': pprint.pprint,
                       },
                optionflags=optionflags,
                ),
            layer=layer,
            )
        for testfile in TESTFILES
        ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')                 #pragma NO COVERAGE
