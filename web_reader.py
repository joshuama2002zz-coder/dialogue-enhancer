"""Fetch public HTML only, with pinned public IPs and bounded redirects/body size."""
import http.client
import ipaddress
import socket
import ssl
from urllib.parse import urlsplit, urljoin

LIMIT=5*1024*1024

def fetch_article(url):
    for _ in range(6):
        parsed=urlsplit(url)
        if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError('请输入公开网页的 http / https 链接。')
        port=parsed.port or (443 if parsed.scheme=='https' else 80)
        if port not in (80,443):raise ValueError('仅支持标准网页端口。')
        host=parsed.hostname.encode('idna').decode()
        addresses=socket.getaddrinfo(host,port,type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
            raise ValueError('不读取本机或内网地址，请使用公开文章链接。')
        ip=addresses[0][4][0]
        connection=http.client.HTTPConnection(host,port,timeout=15)
        sock=socket.create_connection((ip,port),timeout=15)
        if parsed.scheme=='https':
            try:sock=ssl.create_default_context().wrap_socket(sock,server_hostname=host)
            except Exception:sock.close();raise
        connection.sock=sock
        try:
            connection.request('GET',(parsed.path or '/')+('?' + parsed.query if parsed.query else ''),headers={'User-Agent':'Mozilla/5.0 (compatible; DialogueEnhancerReader/1.0)','Accept':'text/html,application/xhtml+xml','Host':host})
            response=connection.getresponse()
            if response.status in (301,302,303,307,308):
                location=response.getheader('Location')
                if not location:raise ValueError('网页跳转缺少目标地址。')
                url=urljoin(url,location);continue
            if response.status!=200:raise ValueError('网站返回 HTTP '+str(response.status)+'，可能需要登录或不允许自动读取。')
            content_type=response.getheader('Content-Type','')
            if 'text/html' not in content_type and 'application/xhtml+xml' not in content_type:
                raise ValueError('目前支持 HTML 网页，不支持 PDF 或其他文件链接。')
            data=response.read(LIMIT+1)
            if len(data)>LIMIT:raise ValueError('页面过大，请选择具体文章链接。')
            charset=response.headers.get_content_charset() or 'utf-8'
            try:html=data.decode(charset,errors='replace')
            except LookupError:html=data.decode('utf-8',errors='replace')
            return {'url':url,'html':html}
        finally:connection.close()
    raise ValueError('网页跳转次数过多。')
