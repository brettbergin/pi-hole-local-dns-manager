from setuptools import setup, find_packages


def get_requirements():
    with open('requirements.txt', 'r') as fp:
        requirements = fp.readlines()
    return requirements


setup(
    name='pihole_manager',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pihole_manager = pihole_manager.main:main'
        ]
    },
    install_requires=get_requirements(),
    description='Manage your internal DNS records for pihole with this utility.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown'
)
