import pymongo, requests, os, datetime, time, hashlib, logging, random
from multiprocessing import Pool, current_process
from requests_toolbelt.adapters import source
import config, tool

logger = tool.logger()
local_ips = tool.get_ip()
s = requests.Session()

def get_data():
   '''从数据库获取数据'''
    conn = pymongo.MongoClient(config.MONGO_HOST, config.MONGO_PORT)
    db = conn.xingchao_spider_db
    product_set = db.tb_product.find({'sid': config.ID})
    yield from product_set

def save_img(url, file_name):
   '''保存图片'''
    dir = os.path.dirname(file_name)
    if not os.path.exists(dir):
        os.makedirs(dir)
    bind_ip = random.choice(local_ips)  # 从本地网卡地址中随机选取一个绑定
    new_src = source.SourceAddressAdapter(bind_ip)
    s.mount('http://', new_src)
    s.mount('https://', new_src)
    pname = current_process().name   # 获取进程名
    logger.info('进程：{0} 开始下载-->{1} 流量出口->【{2}】'.format(pname, url, bind_ip))
    res = s.get(url)
    if res.status_code != 200:
        logger.info('进程：{0} 下载失败-->{1}, code:{2}'.format(pname, url, res.status_code))
    file_tmp = file_name + '_tmp'
    with open(file_tmp, 'wb') as f:
        f.write(res.content)
        try:
            size = os.path.getsize(file_tmp)
            if size > 10000:    # 判断文件完整性
                os.rename(file_tmp, file_name)
        except Exception as e:
            logging.error('保存失败-->', url)
    logger.info('进程：{0} 下载完成-->{1}'.format(pname, file_name))

def md5(url):
    obj = hashlib.md5()
    obj.update(bytes(url, encoding='utf-8'))

    return obj.hexdigest()

def get_path(product):
    '''获取文件保存路径'''
    id = product['_id']
    pid = product['pid']
    url = product['url']
    brand = product['brand']

    if 'image' in product:
        image = product['image']

    dir = url.split('/')[2] + '-' + pid + '_new'
    date = str(datetime.date.fromtimestamp(time.time()))

    for u in image:
        f = u.split('.')[-1]
        if image.index(u) == 0:
            filename = '%s_&_%s.%s' % (brand, id, f)
        else:
            filename = '%s_&_%s_%s.%s' % (brand, id, str(image.index(u)), f)

        img_path = os.path.join('/data/work/new_rule/', config.CATEGORY, dir, config.GENDER, date, brand, filename)

        if not os.path.exists(img_path):
            save_img(u, img_path)
        else:
            logger.info('文件已存在-->{0}'.format(img_path))

'''定义进程池'''
p = Pool(20)
for task in get_data():
    p.apply_async(get_path, args=(task,))

p.close()
p.join()
