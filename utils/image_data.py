from bing_image_urls import bing_image_urls
from urllib.parse import urlparse

def image_data(name):
    try:
        imgUrl = bing_image_urls(name, limit=1)[0]
        parsed = urlparse(imgUrl)
        parts = parsed.netloc.split('.')

        if len(parts) > 2:
            host = '.'.join(parts[-2:])
        else:
            host = parsed.netloc
        
        return {
            'url': imgUrl,
            'host':host
        }
    except Exception as e:
        imgUrl = "/no_image"
        host = "localhost"
        return {
            'url': imgUrl,
            'host':host
        }
    
if __name__ == '__main__':
    print(image_data("test"))