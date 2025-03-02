# 使用Python的cryptography库生成自签名SSL证书
# 这个脚本可以在Windows环境下替代OpenSSL命令

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
import os

def generate_self_signed_cert(key_file="key.pem", cert_file="cert.pem", days_valid=365):
    # 生成私钥
    print("正在生成私钥...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    
    # 设置证书主题信息
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "HTTP2 Demo"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    # 设置证书有效期
    now = datetime.datetime.utcnow()
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        now
    ).not_valid_after(
        now + datetime.timedelta(days=days_valid)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName("localhost")]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # 将私钥写入文件
    print(f"正在将私钥写入 {key_file}...")
    with open(key_file, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # 将证书写入文件
    print(f"正在将证书写入 {cert_file}...")
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    print("自签名SSL证书生成完成！")
    print(f"私钥文件: {os.path.abspath(key_file)}")
    print(f"证书文件: {os.path.abspath(cert_file)}")
    print("\n注意: 由于使用自签名证书，浏览器可能会显示安全警告，可以选择继续访问。")

if __name__ == "__main__":
    print("=== Windows环境下SSL证书生成工具 ===")
    print("这个脚本将生成HTTP/2服务器所需的自签名SSL证书")
    
    # 检查是否已存在证书文件
    if os.path.exists("key.pem") or os.path.exists("cert.pem"):
        overwrite = input("检测到已存在的证书文件，是否覆盖？(y/n): ").lower()
        if overwrite != 'y':
            print("操作已取消")
            exit()
    
    # 生成证书
    generate_self_signed_cert()
    
    print("\n现在您可以运行HTTP/2服务器了:")
    print("python http2_server.py")