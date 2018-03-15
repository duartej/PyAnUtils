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
            'mtgAnUtils':'mtgAnUtils/python'},
        packages = ['PyAnUtils','dvAnUtils','mtgAnUtils' ],
        scripts=['bin/mtgfastfullcmp','bin/lazycmt','bin/rootfile_checker','bin/rootipy',
            'dvAnUtils/bin/dvtrigeff',
            'dvAnUtils/bin/roibasisconverter', 'dvAnUtils/bin/fitmodel',
            'mtgAnUtils/bin/mtg_gs_summary',
            'dvAnUtils/bin/quickTrackPlotter','bin/getdecorations',
            # TO BE DEPRECATED in favour of runDVAna_submit
            'dvAnUtils/bin/ks_submit_prun',
            'dvAnUtils/bin/ks_submit_localbatch',
            'dvAnUtils/bin/kshort_study', ],
        )
