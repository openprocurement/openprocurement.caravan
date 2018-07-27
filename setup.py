from setuptools import setup, find_packages

version = '1.0.0'

requires = [
    'setuptools',
]

test_requires = requires + [
    'webtest',
    'python-coveralls',
]

docs_requires = requires + [
    'sphinxcontrib-httpdomain',
]

entry_points = {
    'console_scripts': [
        'ceasefire_loki_caravan = openprocurement.caravan.runners.ceasefire_loki:main'
    ]
}


setup(name='openprocurement.caravan',
      version=version,
      description="",
      long_description=open("README.md").read(),
      classifiers=[
          "Framework :: Pylons",
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
      ],
      keywords="web services",
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      license='Apache License 2.0',
      url='https://github.com/openprocurement/openprocurement.caravan',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openprocurement', 'openprocurement.caravan'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      extras_require={
          'test': test_requires,
          'docs': docs_requires
      },
      entry_points=entry_points,
      )
