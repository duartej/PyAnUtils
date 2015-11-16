from distutils.core import setup, Extension


setup(name='PyAnUtils',
        version='0.1',
        description='Python Analysis Utils',
        author='Jordi Duarte-Campderros',
        author_email='Jordi.Duarte.Campderros@cern.ch',
        url='https://github.com/duartej/PyAnUtils',
        # See https://docs.python.org/2/distutils/setupscript.html#listing-whole-packages
        # for changes in the package distribution
        package_dir={'PyAnUtils':'python','dvAnUtils':'dvAnUtils/python',
            'jobSender':'jobSender/python','mtgAnUtils':'mtgAnUtils/python'},
        packages = ['PyAnUtils','dvAnUtils','jobSender','mtgAnUtils' ],
        scripts=['bin/mtgfastfullcmp','bin/lazycmt','dvAnUtils/bin/dvtrigeff',
            'dvAnUtils/bin/roibasisconverter', 'dvAnUtils/bin/fitmodel',
            'jobSender/bin/clustermanager','mtgAnUtils/bin/mtg_gs_summary',
            'dvAnUtils/bin/quickTrackPlotter','bin/getdecorations'],
        )
