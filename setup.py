from setuptools import setup

setup(
    name='mkdocs-linkpatcher-plugin',
    version='0.0.1',
    license='MIT',
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    install_requires=[
        "tinydb >= 3.8.0", "markdown >= 2.6.11", "mkdocs >= 0.17.2"
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    packages=['linkpatcher'],
    entry_points={
        'mkdocs.plugins': [
            'linkpatcher-plugin = linkpatcher.plugin:LinkPatcherPlugin',
        ]
    })
