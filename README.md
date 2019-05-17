## let's start
```sh
git clone git@github.com:wuyueCreator/district.git
cd district
pipenv install

# create and init database
flask initdb

flask run

# you will see that:
………………………………………………………………………………………………………………………………………………………………………………………………
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
……………………………………………………………………………………………………………………………………………………………………………………………… 
```

https://github.com/wuyueCreator/district/archive/master.zip
sunzhenqiang@mabao51.net


## 设计方案
- 爬取中华人民共和国民政部官网,获取数据
- 对于直辖市，增加 XX城区，以便统一数据格式
- 将行政区数据按照省/直辖市、市/城区、县依次存储至 Province、City、County，按照归属关系进行关联

- 提供接口
    - initialize
    - update
    - query

