from setuptools import setup, find_packages

pkg_location = 'rtai' # src
pkg_name     = 'rtai'
vfile = './'+pkg_name+'/_version.py'
vers = {}

# Read requirements.txt, ignore comments
try:
    with open("requirements.txt", "r") as f:
        REQUIRES = [line.split('#', 1)[0].strip() for line in f if line.strip()]
except:
    print("'requirements.txt' not found!")
    REQUIRES = list()

with open(vfile) as f:
   exec(f.read(), {}, vers)

with open('README.md') as f:
    long_description = f.read()

setup(name=pkg_name,
      version=vers['__version__'],
      author='J.R. Feibelman',
      author_email='jrfeibelman@gmail.com',
      maintainer_email='jrfeibelman@gmail.com',
      py_modules=[pkg_name],
      description='Simulation agent for generative AI agents',
      long_description=long_description,
      long_description_content_type='text/markdown; charset=UTF-8',
      url='http://github.com/jrfeibelman/WebAI',
      platforms='Mac OSX',
      license="MIT",
      package_dir={'': pkg_location},
      packages=find_packages(where=pkg_location),
      include_package_data=True,
      install_requires=REQUIRES,
      python_requires=">=3.11",
      classifiers=['Development Status :: 3 - Alpha',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: MacOS :: MacOS X',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.11',
                   'Programming Language :: Python :: 3.12',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: BSD License',
                   'Topic :: Scientific/Engineering :: Artificial Intelligence',
                   'Topic :: Scientific/Engineering :: Large Language Models',
                   'Topic :: Scientific/Engineering :: Generative Agents',
                   'Programming Language :: Python :: Implementation :: CPython',
                   ],
      keywords=['Large Language Models', 'generative', 'agents', 'Artificial Intelligence', 'LLM', 'AI'],
      )

