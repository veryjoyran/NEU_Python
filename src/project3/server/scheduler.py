# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from scraper import WebScraper_HouseData

def scheduled_scrape():
    base_url = "https://esf.fang.com/"  # 可以根据需要调整
    scraper = WebScraper_HouseData(base_url=base_url, pages=5)
    scraped_data = scraper.scrape()
    scraper.save_to_db(scraped_data)
    print(f"Scheduled scraping completed. {len(scraped_data)} new records added.")

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_scrape, 'interval', weeks=1)
