from setuptools import setup, find_packages

with open("README.rst") as f:
    long_description = f.read()

setup(name="sumpf",
      version="0.17",
      description="A signal processing package with a focus on acoustics",
      long_description=long_description,
      url="https://github.com/JonasSC/SuMPF",
      author="Jonas Schulte-Coerne",
      license="GNU Lesser General Public License v3 or later (LGPLv3+)",
      classifiers=["Development Status :: 5 - Production/Stable",
                   "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
                   "Programming Language :: Python :: 3.7",
                   "Intended Audience :: Developers",
                   "Intended Audience :: Science/Research",
                   "Topic :: Software Development :: Libraries :: Application Frameworks"],
      keywords="signal-processing acoustics",
      packages=find_packages(exclude=["documentation", "tests", "docs"]),
      install_requires=["numpy", "connectors", "scipy", "SoundFile", "JACK-Client", "numexpr"],
      extras_require={"dev": ["pytest-cov", "pylint"],
                      "test": ["pytest", "hypothesis"]},
      project_urls={"Documentation": "https://sumpf.readthedocs.io/en/latest/",
                    "Bug Reports": "https://github.com/JonasSC/SuMPF/issues",
                    "Source": "https://github.com/JonasSC/SuMPF"})
