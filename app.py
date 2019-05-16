from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import click
from spider import DistrictData

app = Flask(__name__)

# sqllite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
# mysql
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:19940619_Wbb@localhost:3306/test'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text)

    def __repr__(self):
        return '{}:{}'.format(self.id, self.title)


class Province(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area_code = db.Column(db.Integer, unique=True)
    name = db.Column(db.Text)

    def __repr__(self):
        return '{}:{}'.format(self.area_code, self.name)

    def to_json(self):
        return {
            'id': self.area_code,
            'name': self.name,
            'districts': []
        }


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    province_id = db.Column(db.Integer, db.ForeignKey('province.id'))
    area_code = db.Column(db.Integer, unique=True)
    name = db.Column(db.Text)

    def __repr__(self):
        return '{}:{}'.format(self.area_code, self.name)

    def to_json(self):
        return {
            'id': self.area_code,
            'name': self.name,
            'districts': []
        }


class County(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    area_code = db.Column(db.Integer, unique=True)
    name = db.Column(db.Text)

    def __repr__(self):
        return '{}:{}'.format(self.area_code, self.name)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'districts': []
        }


@app.cli.command()
def initdb():
    db.drop_all()
    click.echo("Dropped database")
    db.create_all()
    click.echo("Initialized database")


def what(district):
    id_str = str(district["id"]).strip('0')
    if len(id_str) < 3:
        return Province(area_code=district["id"], name=district["name"])
    elif len(id_str) < 5:
        province = Province.query.filter(Province.area_code == int('{:0<2d}0000'.format(int(str(district["id"])[:2]))))
        return City(area_code=district["id"], name=district["name"],
                    province_id=province[0].id) if province.count() else None
    else:
        city = City.query.filter(City.area_code == int('{:0<4d}00'.format(int(str(district["id"])[:4]))))

        return County(area_code=district["id"], name=district["name"],
                      city_id=city[0].id) if city.count() else None


def query(keywords="", id_area=0):
    if keywords:
        return [x.to_json() for x in Province.query.filter(Province.name.like("%{}%".format(keywords)))] + \
               [x.to_json() for x in City.query.filter(City.name.like("%{}%".format(keywords)))] + \
               [x.to_json() for x in County.query.filter(County.name.like("%{}%".format(keywords)))]
    if id_area:
        return [x.to_json() for x in Province.query.filter_by(area_code=id_area)] or \
               [x.to_json() for x in City.query.filter_by(area_code=id_area)] or \
               [x.to_json() for x in County.query.filter_by(area_code=id_area)]


def get_next(district):
    id_str = str(district["id"]).strip('0')
    if len(id_str) < 3:
        return [x.to_json() for x in
                City.query.filter_by(province_id=Province.query.filter_by(area_code=district["id"]).first().id)]
    elif len(id_str) < 5:
        return [x.to_json() for x in
                County.query.filter_by(city_id=City.query.filter_by(area_code=district["id"]).first().id)]
    else:
        return []


def get_district(district, depth=1):
    if depth == 1:
        return district
    if depth > 1:
        for item in district:
            item["districts"] = get_next(item)
            if depth > 2:
                for _item in item["districts"]:
                    _item["districts"] = get_next(_item)
    return district


@app.route('/initialize', methods=['GET'])
def initialize():
    with app.app_context():
        if Province.query.count():
            return jsonify({
                "code": 1001,
                "message": "数据已初始化"
            })
        districts = DistrictData()()
        session = db.session.registry()
        for district in districts:
            temp = what(district)
            if temp:
                session.add(temp)
            if isinstance(temp, (Province, City)):
                session.commit()
        session.commit()
        # add history
        session.add(History(url=DistrictData().get_url()))
        session.commit()

        return jsonify({
            "code": 0,
            "message": "SUCCESS",
            "data": {
                "number": Province.query.count() + City.query.count() + County.query.count()
            }
        })


@app.route('/query', methods=['GET'])
def get_data():
    keywords = request.args.get('keywords') or ""
    id_area = int(request.args.get('id') or '0')
    depth = int(request.args.get('depth') or '1')

    district = query(keywords=keywords, id_area=id_area)
    if district:
        get_district(district, depth=depth)
        return jsonify({
            "code": 0,
            "message": "SUCCESS",
            "data": {
                "districts": district
            }
        })
    return jsonify({
            "code": 1003,
            "message": "请输入查询条件"
        })


# 粗暴简单更新法
@app.route('/update', methods=['GET'])
def update():
    url = str(DistrictData().get_url()).strip()
    if History.query.filter_by(url=url).count():
        return jsonify({
            "code": 1002,
            "message": "无新数据",
        })

    db.drop_all()
    db.create_all()
    initialize()
    return jsonify({
        "code": 0,
        "message": "SUCCESS",
        "data": {
            "number": Province.query.count() + City.query.count() + County.query.count(),
            "url": url
        }
    })


if __name__ == '__main__':
    app.run()
