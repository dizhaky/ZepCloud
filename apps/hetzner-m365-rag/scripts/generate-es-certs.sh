#!/bin/bash
# Generate Self-Signed SSL Certificates for Elasticsearch
# Run this before starting docker-compose for the first time

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔐 Generating Elasticsearch SSL Certificates${NC}"
echo ""

# Configuration
CERT_DIR="config/elasticsearch/certs"
DAYS_VALID=3650  # 10 years

# Create certificate directory
mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

echo -e "${YELLOW}📝 Configuration:${NC}"
echo "  Certificate directory: $CERT_DIR"
echo "  Validity: $DAYS_VALID days (10 years)"
echo "  Nodes: elasticsearch (172.28.0.10)"
echo ""

# Check if certificates already exist
if [ -f "elasticsearch.crt" ]; then
    echo -e "${YELLOW}⚠️  Certificates already exist${NC}"
    read -p "Regenerate? This will require restarting Elasticsearch (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo "Cancelled."
        exit 0
    fi
    echo -e "${YELLOW}🗑️  Removing old certificates...${NC}"
    rm -f ca.key ca.crt elasticsearch.key elasticsearch.csr elasticsearch.crt
fi

# Step 1: Generate CA (Certificate Authority)
echo -e "${YELLOW}1️⃣  Generating Certificate Authority (CA)...${NC}"
openssl genrsa -out ca.key 4096

openssl req -new -x509 -days $DAYS_VALID -key ca.key -out ca.crt \
    -subj "/C=US/ST=State/L=City/O=M365-RAG/OU=Infrastructure/CN=M365-RAG-CA"

echo -e "${GREEN}✅ CA certificate generated${NC}"

# Step 2: Generate Elasticsearch private key
echo -e "${YELLOW}2️⃣  Generating Elasticsearch private key...${NC}"
openssl genrsa -out elasticsearch.key 4096
echo -e "${GREEN}✅ Private key generated${NC}"

# Step 3: Create certificate signing request (CSR)
echo -e "${YELLOW}3️⃣  Creating certificate signing request (CSR)...${NC}"

# Create OpenSSL configuration for SANs
cat > elasticsearch.cnf <<EOF
[req]
default_bits = 4096
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C = US
ST = State
L = City
O = M365-RAG
OU = Elasticsearch
CN = elasticsearch

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = elasticsearch
DNS.2 = localhost
IP.1 = 172.28.0.10
IP.2 = 127.0.0.1
EOF

openssl req -new -key elasticsearch.key -out elasticsearch.csr \
    -config elasticsearch.cnf

echo -e "${GREEN}✅ CSR created${NC}"

# Step 4: Sign certificate with CA
echo -e "${YELLOW}4️⃣  Signing certificate with CA...${NC}"
openssl x509 -req -days $DAYS_VALID -in elasticsearch.csr \
    -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out elasticsearch.crt \
    -extensions v3_req -extfile elasticsearch.cnf

echo -e "${GREEN}✅ Certificate signed${NC}"

# Step 5: Set proper permissions
echo -e "${YELLOW}5️⃣  Setting file permissions...${NC}"
chmod 644 ca.crt elasticsearch.crt
chmod 600 ca.key elasticsearch.key
rm elasticsearch.csr elasticsearch.cnf ca.srl 2>/dev/null || true

echo -e "${GREEN}✅ Permissions set${NC}"

# Step 6: Verify certificates
echo -e "${YELLOW}6️⃣  Verifying certificates...${NC}"
openssl verify -CAfile ca.crt elasticsearch.crt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Certificate verification successful${NC}"
else
    echo -e "${RED}❌ Certificate verification failed${NC}"
    exit 1
fi

# Display certificate information
echo ""
echo -e "${GREEN}📋 Certificate Information:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
openssl x509 -in elasticsearch.crt -noout -subject -issuer -dates -ext subjectAltName

echo ""
echo -e "${GREEN}🎉 SSL Certificates Generated Successfully!${NC}"
echo ""
echo -e "${YELLOW}📁 Generated files:${NC}"
echo "  - ca.crt (Certificate Authority)"
echo "  - ca.key (CA Private Key)"
echo "  - elasticsearch.crt (Elasticsearch Certificate)"
echo "  - elasticsearch.key (Elasticsearch Private Key)"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "  1. Certificates are ready at: $CERT_DIR"
echo "  2. Start Elasticsearch: docker compose up -d elasticsearch"
echo "  3. Verify SSL: curl -k -u elastic:PASSWORD https://localhost:9200"
echo ""
echo -e "${GREEN}✅ You're ready to start Elasticsearch with SSL enabled!${NC}"

