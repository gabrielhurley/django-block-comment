from setuptools import setup, find_packages

setup(name='django-block-comment',
    version='1.0',
    description='A drop-in solution for providing block-level commenting capabilities on arbitrary chunks of marked-up text.',
    long_description=open('README.rst').read(),
    author='Gabriel Hurley',
    author_email='gabriel@strikeawe.com',
    license='BSD',
    url='https://github.com/gabrielhurley/django-block-comment',
    download_url='git://github.com/gabrielhurley/django-block-comment.git',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
   ],
)