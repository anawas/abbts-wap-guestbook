# Zuerst Package cryptography installieren:
# pip install cryptography

import datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)
from cryptography.x509.oid import NameOID

# Generiere einen privaten Schlüssel
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Speichere den privaten Schlüssel in einer Datei
with open("mydomain.key", "wb") as key_file:
    key_file.write(
        private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=NoEncryption(),
        )
    )

# Erstelle ein selbstsigniertes Zertifikat
subject = issuer = x509.Name(
    [
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CH"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Aargau"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Baden"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ABB TS"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ]
)
cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(private_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.utcnow())
    .not_valid_after(
        # Gültig für 1 Jahr
        datetime.datetime.utcnow()
        + datetime.timedelta(days=365)
    )
    .add_extension(
        x509.SubjectAlternativeName([x509.DNSName("localhost")]),
        critical=False,
    )
    .sign(private_key, hashes.SHA256())
)

# Speichere das Zertifikat in einer Datei
with open("mydomain.crt", "wb") as cert_file:
    cert_file.write(cert.public_bytes(serialization.Encoding.PEM))

print(
    "Private key and self-signed certificate have been generated "
    + "and saved as 'mydomain.key' and 'mydomain.crt'."
)
