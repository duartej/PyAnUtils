from distutils.core import setup, Extension

setup(name='PyAnUtils',
		version='0.1',
		description='Python Analysis Utils',
		author='Jordi Duarte-Campderros',
		author_email='Jordi.Duarte.Campderros@cern.ch',
		url='https://github.com/',
		# See https://docs.python.org/2/distutils/setupscript.html#listing-whole-packages
		# for changes in the package distribution
        package_dir={'PyAnUtils':'python','dvAnUtils':'python/dvAnUtils'},
		packages = ['PyAnUtils','dvAnUtils' ],
		scripts=['bin/mtgfastfullcmp','bin/lazycmt','bin/clustermanager','python/dvAnUtils/bin/dvtrigeff'],
		)
