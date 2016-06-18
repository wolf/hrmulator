from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='hrmulator',
      version='0.1',
      description='a simple computer, programmable in its own assembly language',
      url='http://github.com/wolf/hrmulator',
      author='Wolf',
      author_email='Wolf@zv.cx',
      license='MIT',
      packages=['hrmulator'],
      install_requires=[
        'colorama',
        'termcolor',
      ],
      test_suite='nose.collector',
      tests_require=[
        'mock',
        'nose',
      ],
      zip_safe=False)
