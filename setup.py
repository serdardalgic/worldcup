from distutils.core import setup


setup(
    name='worldcup',
    version='1.0.1',
    author_email='fatiherikli@gmail.com',
    py_modules=['worldcup'],
    entry_points={
        'console_scripts': [
            'worldcup = worldcup:main',
        ],
    },
    install_requires=[
        'python-dateutil>=1.5',
        'colorama==0.3.1',
        'pytz==2014.4',
        'humanize==0.5'
    ],
    classifiers=[
      'Environment :: Console'
    ],
)
