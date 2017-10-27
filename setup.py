from setuptools import setup

setup(name='seqio',


      packages=['seqio',
                ],
      entry_points={
          'console_scripts': [
              'seqio = seqio.cli:main',
          ]
      },
      install_requires=['six', 'biopython']
      )
