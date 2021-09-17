from setuptools import setup

package_name = 'cam2image_to_kvs'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Tokuro Kono',
    maintainer_email='tokuro_kono@r.recruit.co.jp',
    description='Send image to AWS Kinesis Video Stream',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'cam2image_to_kvs_node = '
            'cam2image_to_kvs.cam2image_to_kvs_node:main'
        ],
    },
)
