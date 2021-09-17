# Copyright (c) Recruit Co., Ltd.
# Refer to LICENSE file for the full copyright and license information

import argparse

import boto3
import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class ImageListener(Node):

    def __init__(
            self, stream_name, accesskey, secretkey, region, width, height):
        super().__init__("CameraImageListener")
        self.create_subscription(Image, "image", self.callback)
        self.cvBridge = CvBridge()
        self.width = width
        self.height = height
        framerate = 5/1

        sink = \
            'appsrc do-timestamp=TRUE ! videoconvert ' + \
            f'! video/x-raw,format=I420,width={self.width},' + \
            f'height={self.height},framerate=5/1 ' + \
            '! x264enc  bframes=0 key-int-max=45 bitrate=500 ' + \
            '! video/x-h264,stream-format=avc,alignment=au,' + \
            'profile=baseline ' + \
            f'! kvssink stream-name="{stream_name}" storage-size=512 ' + \
            f'access-key="{accesskey} secret-key="{secretkey} ' + \
            f'aws-region="{region}"'

        print(sink)

        self.out = cv2.VideoWriter(sink, 0, framerate, (width, height))

    def callback(self, msg):
        try:
            # Convert to numpy array
            cv_image = self.cvBridge.imgmsg_to_cv2(msg, "bgr8")
            h, w, _ = cv_image.shape
            send_image = None

            if self.width == w and self.height == h:
                send_image = cv_image
                self.out.write(cv_image)
            else:
                rw = self.width / w
                rh = self.height / h
                send_image = cv2.resize(cv_image, (int(w * rw), int(h * rh)))

            self.out.write(send_image)
        except Exception as e:
            print(e)


def main():
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Send image to AWS Kinesis Video Stream",
    )

    parser.add_argument(
        "--stream-name", "-n", dest="stream_name", required=True,
        help="(Required) Stream name in AWS Kinesis Video Stream."
    )
    parser.add_argument(
        "--accesskey", "-a", dest="accesskey", required=True,
        help="(Required) AWS Access Key."
    )
    parser.add_argument(
        "--secretkey", "-s", dest="secretkey", required=True,
        help="(Required) AWS Secret Key."
    )
    parser.add_argument(
        "--region", "-r", dest="region", default="ap-northeast-1",
        help="(Required) AWS KVS Region."
    )
    parser.add_argument(
        "--width", "-w", dest="width", default="640", type=int,
        help="(Optional: Default=640) Width of the image sent to KVS."
    )
    parser.add_argument(
        "--height", "-h", dest="height", default="480", type=int,
        help="(Optional: Default=480) Height of the image sent to KVS."
    )

    args = parser.parse_args()

    rclpy.init()
    node = ImageListener(
        stream_name=args.stream_name, accesskey=args.accesskey,
        secretkey=args.secretkey, region=args.region,
        width=args.width, height=args.height
    )

    rclpy.spin(node)

    # cv2.destroyAllWindows()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
