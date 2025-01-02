# server/app.py
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from scraper import WebScraper_HouseData
from database import Session, House
from scheduler import scheduler
from sqlalchemy import func
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)
CORS(app)

class Scrape(Resource):
    def post(self):
        data = request.get_json()
        city_code = data.get('city_code')
        pages = data.get('pages', 5)
        if not city_code:
            logger.warning("城市代码缺失")
            return {"message": "city_code is required"}, 400
        base_url = f"https://{city_code}.esf.fang.com/" if city_code != "bj" else "https://esf.fang.com/"
        scraper = WebScraper_HouseData(base_url=base_url, pages=pages)
        scraped_data = scraper.scrape()
        if not scraped_data:
            logger.info("没有爬取到任何数据")
            return {"message": "没有爬取到任何数据。"}, 200
        scraper.save_to_db(scraped_data)
        data_count = len(scraped_data)
        logger.info(f"数据爬取并保存成功，新增 {data_count} 条记录。")
        return {
            "message": f"数据爬取并保存成功，新增 {data_count} 条记录。",
            "data_count": data_count
        }, 200

class Houses(Resource):
    def get(self):
        session = Session()
        houses = session.query(House).all()
        session.close()
        data = [{
            "room_type": house.room_type,
            "area": house.area,
            "floor": house.floor,
            "orientation": house.orientation,
            "build_year": house.build_year,
            "owner_name": house.owner_name,
            "address": house.address,
            "description": house.description,
            "price": house.price
        } for house in houses]
        return jsonify(data)

class Statistics(Resource):
    def get(self):
        session = Session()
        try:
            count = session.query(House).count()
            # 按房型统计数量
            stats = session.query(House.room_type, func.count(House.id)).group_by(House.room_type).all()
            stats_dict = {room_type: cnt for room_type, cnt in stats}
            logger.info("统计数据获取成功")
            return jsonify({"total": count, "statistics": stats_dict})
        except Exception as e:
            logger.error(f"获取统计数据时出错: {e}")
            return {"message": f"An error occurred: {str(e)}"}, 500
        finally:
            session.close()

api.add_resource(Scrape, '/api/scrape')
api.add_resource(Houses, '/api/houses')
api.add_resource(Statistics, '/api/statistics')

if __name__ == '__main__':
    scheduler.start()
    app.run(host='0.0.0.0', port=5000)
