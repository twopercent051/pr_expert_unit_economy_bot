import requests

url = "https://www.ozon.ru/product/venchik-dlina-30-sm-1032535756/?advert=aIVH45yTMtC_FXDSvVchO1xTnk1w0ZB3jcF2FsTgC3k-kyg3e1MFf-ePHrti-XhUD0-nFHmtewpUuLz-3MQNyy6eTEXTuzEhQGSV1pHPDW8j9T7hlwPrDFcyTkRfe3wBcmcnxELUC1Sh1n_alm21uNj-nGL_2S8S&avtc=1&avte=2&avts=1691525965&sh=DnIuHjDvTw"
ret = requests.get("http://92.255.110.184:8888/api/v1/cards",
                   headers={"Accept": "application / json"},
                   params=dict(url=url),
                   timeout=100)
print(ret.status_code)
try:
    print(ret.json())
except Exception as e:
    print(e)
