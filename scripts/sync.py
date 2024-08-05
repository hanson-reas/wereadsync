import argparse
import json
import os
import pendulum
from retrying import retry
import requests
from notion_helper import NotionHelper
import utils
from dotenv import load_dotenv

load_dotenv()

def insert_to_notion(database_id,title,parent_database_id=None):
    parent = {
        "database_id": database_id,
        "type": "database_id",
    }
    properties = {
        "实多性识辨": {"title": [{"type": "text", "text": {"content": title}}]},
    }
    if parent_database_id:
        properties["融通性识辨"] = utils.get_relation([parent_database_id])
    page_id= notion_helper.create_page(
        parent=parent,
        properties=properties,
    ).get("id")
    return page_id

def update_sync_status(page_id):
    properties = {
        "已同步": {"checkbox": True},
    }
    notion_helper.update_page(
        page_id=page_id,
        properties=properties,
    )

if __name__ == "__main__":
    notion_helper = NotionHelper()
    from_pages = os.getenv("FROM_PAGE").strip().split(",")
    to_page = os.getenv("TO_PAGE").strip()
    to_database_id = notion_helper.extract_page_id(to_page)
    results = []
    for page in from_pages:
        database_id = notion_helper.extract_page_id(page)
        filter = {"property": "已同步", "checkbox": {"equals": False}}
        results.extend(notion_helper.query_all_by_filter(database_id=database_id,filter=filter))
    for index,result in enumerate(results):
        print(f"共{len(results)}条数据，正在同步第{index+1}条数据")
        properties = result.get("properties")
        title = utils.get_property_value(properties.get("Name"))
        parent_page_id = insert_to_notion(database_id=to_database_id,title=title)
        if "abstract" in properties:
            abstract = utils.get_property_value(properties.get("abstract"))
            insert_to_notion(database_id=to_database_id,title=abstract,parent_database_id=parent_page_id)
        update_sync_status(page_id=result.get("id"))

