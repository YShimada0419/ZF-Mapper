from setuptools import setup, find_packages

setup(name='zfmapper',
      version='0.0.1',
      description='Python setuptools helloworld',
      author='Name',
      author_email='name@example.jp',
      url='https://github.com/',
      packages=find_packages(),
      install_requires=["tifffile"]
      entry_points="""
      [console_scripts]
      zfmapper = zfmapper.zfmapper:main
      """,)
