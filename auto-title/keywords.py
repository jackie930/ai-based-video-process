from boto3.session import Session
import json

def extract_textrank(input_csv):
    data = {
        "data": "《半導體》Q1展望保守，世界垂淚2019/02/11 10:28時報資訊【時報記者沈培華台北報導】世界先進 (5347) 去年營運創歷史新高，每股純益達3.72元。但對今年首季展望保守，預計營收將比上季高點減近一成。世界先進於封關前股價拉高，今早則是開平走低。世界先進於年前台股封關後舉行法說會公布財報。公司去年營運表現亮麗，營收與獲利同創歷史新高紀錄。2018年全年營收289.28億元，年增16.1%，毛利率35.2%，拉升3.2個百分點，稅後淨利61.66億元，年增36.9%，營收與獲利同創歷史新高，每股純益3.72元。董事會通過去年度擬配發現金股利3.2元。展望第一季，受到客戶進入庫存調整，公司預期，本季營收估在67億至71億元，將季減8%至13%，毛利率將約34.5%至36.5%。此外，因應客戶需求，世界先進決定斥資2.36億美元，收購格芯新加坡8吋晶圓廠。世界先進於年前宣布，將購買格芯位於新加坡Tampines的8吋晶圓3E廠房、廠務設施、機器設備及微機電(MEMS)智財權與業務，交易總金額2.36億美元，交割日訂108年12月31日。格芯晶圓3E廠現有月產能3.5萬片8吋晶圓，世界先進每年將可增加超過40萬片8吋晶圓產能，增進公司明年起業績成長動能。TOP關閉"}

    session = Session()

    runtime = session.client("runtime.sagemaker")
    response = runtime.invoke_endpoint(
        EndpointName='textrank',
        ContentType="application/json",
        Body=json.dumps(data),
    )

    result = json.loads(response["Body"].read())
    print (result)

if __name__ == '__main__':
    extract_textrank(input_csv)