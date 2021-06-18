echo $#  'download data from s3'
mkdir videos
aws s3 cp s3://datalab2021/huatai/ ./videos/ --recursive

echo "--finish generate images --"