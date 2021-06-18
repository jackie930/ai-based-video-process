### auto - cut off
# ppt文件自动拆条, 打小标题

import time
from boto3.session import Session
import json
import cv2
import numpy
from PIL import Image, ImageDraw, ImageFont
import boto3
from botocore.config import Config
import pandas as pd
import os

config = Config(
    read_timeout=120,
    retries={
        'max_attempts': 0
    }
)


def cut_frame(video):
    # cut frame if this is a powerpoint
    cap = cv2.VideoCapture(video)
    c = 1
    frameRate = 100  # 帧数截取间隔（每隔100帧截取一帧）
    label_ls = []
    frame_ls = []
    second_ls = []

    while (True):
        ret, frame = cap.read()
        milliseconds = cap.get(cv2.CAP_PROP_POS_MSEC)

        if ret:
            if (c % frameRate == 0):
                # if(c < 10):
                print("开始截取视频第：" + str(c) + " 帧")
                # 这里就可以做一些操作了：显示截取的帧图片、保存截取帧到本地
                # cut off sub titles
                img = frame[0:50, 150:800]
                # upload to s3, back label information
                output_s3_bucket = 'datalab2021'
                output_s3_prefix = 'huatai/pics_refined'

                cv2.imwrite("./capture_refined/" + str(c) + '.jpg', img)
                upload_key = output_s3_prefix + '/' + "./capture_refined/" + str(c) + '.jpg'
                session = Session(region_name='us-west-2')
                s3 = session.client("s3")
                s3.upload_file(Filename="./capture_refined/" + str(c) + '.jpg', Key=upload_key, Bucket=output_s3_bucket)
                try:
                    label = infer(output_s3_bucket, upload_key)
                    frame = cv2ImgAddText(frame, '标题: ' + label, 800, 100, (0, 0, 139), 20)
                    cv2.imwrite("./output/" + str(c) + '.jpg', frame)  # 这里是将截取的图像保存在本地
                    frame_ls.append(c)
                    label_ls.append(label)
                    second_ls.append(milliseconds)

                except:
                    cv2.imwrite("./output/" + str(c) + '.jpg', frame)  # 这里是将截取的图像保存在本地
                    frame_ls.append(c)
                    label_ls.append(' ')
                    second_ls.append(milliseconds)

            c += 1
            cv2.waitKey(0)
        else:
            print("所有帧都已经保存完成")

            df = pd.DataFrame({'frame': frame_ls, 'sub-title': label_ls, 'milliseconds': second_ls})
            num_agg = {'frame': ['min', 'max'], 'milliseconds': ['min', 'max']}
            res = df.groupby('sub-title').agg(num_agg).reset_index()
            print (res)
            res.to_csv('output.csv', encoding='utf-8')

            break

    cap.release()


def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=20):
    if (isinstance(img, numpy.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        "ch_standard.ttf", textSize, encoding="utf-8")
    # 绘制文本
    draw.text((left, top), text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)


def generate_back()
    fps = 30

    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')

    video_writer = cv2.VideoWriter(filename='./result.avi', fourcc=fourcc, fps=fps, frameSize=(1280, 720))

    for i in imgs:
        img = cv2.imread(os.path.join('./output', i))

        cv2.waitKey(100)

        video_writer.write(img)

        print(os.path.join('./output', i) + ' done!')

    video_writer.release()
    print ("success generate result!")


def video_cutoff():


def infer(bucket, input_image):
    image_uri = input_image
    test_data = {
        'bucket': bucket,
        'image_uri': image_uri,
        'content_type': "application/json",
    }
    payload = json.dumps(test_data)
    print(payload)

    sagemaker_runtime_client = boto3.client('sagemaker-runtime', config=config)
    session = Session(sagemaker_runtime_client)

    #     runtime = session.client("runtime.sagemaker",config=config)
    response = sagemaker_runtime_client.invoke_endpoint(
        EndpointName='ocr-endpoint-paddlev2',
        ContentType="application/json",
        Body=payload)

    result = json.loads(response["Body"].read())

    return result['label'][0]


if __name__ == '__main__':
    start = time.clock()
    cut_frame("./videos/qC2ZyaTeVc4A.mkv")
    t1 = time.clock() - start
    print("------程序耗时操作-----------")
    print(t1)