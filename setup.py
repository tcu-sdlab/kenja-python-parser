from setuptools import setup, find_packages

setup(name='kenja-python-parser',
      version='0.1',
      description='Python parser for Kenja Historage',
      author='Kenji Fujiwara',
      author_email='kenji-f@is.naist.jp',
      url='https://github.com/sdlab-naist/kenja-python-parser',
      packages=find_packages(),
      install_requires = ["astor"],
      license="MIT license",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Science/Resarch',
          'License :: OSI Approved :: MIT License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Software Development :: Libraries',
          'Topic :: Utilities',
      ]
)
