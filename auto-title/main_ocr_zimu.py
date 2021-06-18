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
    frameRate = 10  # 帧数截取间隔（每隔100帧截取一帧）
    label_ls = []
    frame_ls = []
    second_ls = []

    while (True):
        ret, frame = cap.read()
        milliseconds = cap.get(cv2.CAP_PROP_POS_MSEC)

        if ret:
            if (c % frameRate == 0):
            #if(c == 1000):
                print("开始截取视频第：" + str(c) + " 帧")
                # 这里就可以做一些操作了：显示截取的帧图片、保存截取帧到本地
                # cut off zimu
                img = frame

                # upload to s3, back label information
                output_s3_bucket = 'datalab2021'
                output_s3_prefix = 'huatai/zimu_refined'

                cv2.imwrite("./zimu/capture_refined/" + str(c) + '.jpg', img)
                upload_key = output_s3_prefix + '/' + "./zimu/capture_refined/" + str(c) + '.jpg'
                session = Session(region_name='us-west-2')
                s3 = session.client("s3")
                s3.upload_file(Filename="./zimu/capture_refined/" + str(c) + '.jpg', Key=upload_key, Bucket=output_s3_bucket)
                try:
                    result = infer(output_s3_bucket, upload_key)
                    #print ("result:", result)
                    label = get_left_corner_bbox(result)
                    #print ("label: ", label)
                    frame_ls.append(c)
                    label_ls.append(label)
                    second_ls.append(milliseconds)
                except:
                    frame_ls.append(c)
                    label_ls.append(' ')
                    second_ls.append(milliseconds)

            c += 1
            cv2.waitKey(0)
        else:
            print("所有视频都已经保存完成")

            df = pd.DataFrame({'frame': frame_ls, 'sub-zimu': label_ls, 'milliseconds': second_ls})
            num_agg = {'frame': ['min', 'max'], 'milliseconds': ['min', 'max']}
            res = df.groupby('sub-zimu').agg(num_agg).reset_index()
            print (res)
            res.to_csv('zimu.csv', encoding='utf-8')

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

def get_left_corner_bbox(result):
    x_ls = []
    y_ls = []
    for i in result['bbox']:
        xmin,ymin = i[0][0],i[1][1]
        x_ls.append(xmin)
        y_ls.append(ymin)

    #print (x_ls)
    #print (y_ls)

    to_remove = []
    for i in range(len(y_ls)):
        if y_ls[i]<(result['shape'][0]/3*2):
            to_remove.append(x_ls[i])

    x_ls_cp = x_ls.copy()

    for i in to_remove:
        x_ls.remove(i)


    return result['label'][x_ls_cp.index(min(x_ls))]
def generate_back():
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

    return result


if __name__ == '__main__':
    start = time.clock()
    cut_frame("./videos/20210123082823.mp4")
    t1 = time.clock() - start
    print("------程序耗时操作-----------")
    print(t1)