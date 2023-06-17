import time
import json
from dataclasses import dataclass, field
import httpx


url = 'https://www.allbirds.com/products.json?limit=250&page={}'
pre = 'https://www.allbirds.com/products/'
save_file = 'all_birds.json'

links = []
extracted_data_objects_list = []


def save_data():

    json_object = json.dumps(
        [item.__dict__ for item in extracted_data_objects_list], indent=4
    )

    with open(save_file, 'w') as outfile:
        outfile.write(json_object)


@dataclass
class DataRaw:
    id: str
    title: str = field(default="")
    color: str = field(default="")
    published_at: str = field(default="")
    vendor: str = field(default="")
    product_type: str = field(default="")

    edition: str = field(default="")
    gender: str = field(default="")
    hue: str = field(default="")
    material: str = field(default="")
    price_tier: str = field(default="")
    silhouette: str = field(default="")

    variants: list = field(default=list)

    images: list = field(default=list)

    url: str = field(default="")


def parse_data(node, product_num):

    if node['title'] == 'Digital Gift Cards':
        return

    raw = DataRaw(

        id=node['id'],
        title=node['title'].split('-')[0].strip(),
        color=node['title'].split('-')[1].strip(),
        published_at=str(node['published_at'][:10]),
        vendor=node['vendor'],
        product_type=node['product_type'],

        hue='',

        variants=[
            {
                'size': variant['title'],
                'available': variant['available'],
                'price': variant['price'],
                'grams': variant['grams'],
                'old_price': variant['compare_at_price']
            }
            for variant in node['variants']
        ],

        images=[
            img['src']
            for img in node['images']
        ],

        url=pre + node['handle']

    )

    tags = node['tags']
    for tag in tags:
        if 'edition' in tag:
            try:
                raw.edition = tag.split('=>')[1].strip()
            except:
                pass
        if 'gender' in tag:
            try:
                raw.gender = tag.split('=>')[1].strip()
            except:
                pass
        if 'hue' in tag:
            try:
                raw.hue = raw.hue + " " + tag.split('=>')[1].strip()
            except:
                pass
        if 'material' in tag:
            try:
                raw.material = tag.split('=>')[1].strip()
            except:
                pass
        if 'price-tier' in tag:
            try:
                raw.price_tier = tag.split('=>')[1].strip()
            except:
                pass
        if 'silhouette' in tag:
            try:
                raw.silhouette = tag.split('=>')[1].strip()
            except:
                pass

    raw.hue = raw.hue.strip()

    extracted_data_objects_list.append(raw)

    # print(f'{raw.product_type} - {raw.gender} - {raw.silhouette}')

    # print('\b\b\b\b'+str(product_num), end='')


def get_data():

    with httpx.Client() as client:

        page_num = 1
        product_num = 1

        while True:

            r = client.get(url.format(page_num))

            products = r.json()['products']

            if len(products) > 0:

                print(f"\nPage {page_num} Have {len(products)} Item")

                for product in products:
                    parse_data(product, product_num)
                    product_num += 1

                page_num += 1

            else:
                break

        print(f'\nTotal Scraped Products => {product_num-1}')


get_data()
save_data()
