from setuptools import setup

with open("README.md", "r", encoding="utf8", errors='ignore') as fh:
    long_description = fh.read()

setup(name='cosbo',
      version='0.0.1',
      description='Surrogate-based optimization package for constrained, expensive to evaluate, black-box optimization problems',
      url='http://https://github.com/lf-santos/cosbo',
      author='Lucas F. Santos',
      author_email='lfs.francisco.95@gmal.com',
      license='MIT',
      packages=['cosbo'],
      install_requires=['numpy',
                        'scikit-learn',
                        'matplotlib',
                        ],
      extras_require = {
          "dev": [
              "build",
              "twine",
              "sphinx",
              "sphinx_rtd_theme",
              "check-manifest",
          ],
          "dwsim": [
              "dwsimopt",
          ],
      },
      long_description=long_description,
      long_description_content_type="text/markdown",
)