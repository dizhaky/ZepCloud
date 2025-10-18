#!/bin/bash

# Azure AI Search RAG Setup Script
# Automates Azure infrastructure creation for TypingMind RAG integration

set -e

# Configuration
RESOURCE_GROUP="typingmind-rag-rg"
LOCATION="eastus"  # Change to your preferred region
SEARCH_SERVICE_NAME="typingmind-search-$(whoami | tr '[:upper:]' '[:lower:]')"
STORAGE_ACCOUNT_NAME="tmstorage$(date +%s | tail -c 8)"
CONTAINER_NAME="training-data"
INDEX_NAME="training-data-index"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if Azure CLI is installed
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI is not installed. Please install it first:"
        echo "  brew install azure-cli"
        echo "  or visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi

    # Check if logged in to Azure
    if ! az account show &> /dev/null; then
        log_error "Not logged in to Azure. Please run: az login"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Create resource group
create_resource_group() {
    log_info "Creating resource group: $RESOURCE_GROUP"

    if az group show --name "$RESOURCE_GROUP" &> /dev/null; then
        log_warning "Resource group $RESOURCE_GROUP already exists"
    else
        az group create \
            --name "$RESOURCE_GROUP" \
            --location "$LOCATION" \
            --output table
        log_success "Resource group created"
    fi
}

# Create AI Search service
create_search_service() {
    log_info "Creating AI Search service: $SEARCH_SERVICE_NAME"

    if az search service show --name "$SEARCH_SERVICE_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        log_warning "Search service $SEARCH_SERVICE_NAME already exists"
    else
        az search service create \
            --name "$SEARCH_SERVICE_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --sku free \
            --location "$LOCATION" \
            --output table
        log_success "AI Search service created"
    fi
}

# Create storage account
create_storage_account() {
    log_info "Creating storage account: $STORAGE_ACCOUNT_NAME"

    if az storage account show --name "$STORAGE_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        log_warning "Storage account $STORAGE_ACCOUNT_NAME already exists"
    else
        az storage account create \
            --name "$STORAGE_ACCOUNT_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --location "$LOCATION" \
            --sku Standard_LRS \
            --kind StorageV2 \
            --output table
        log_success "Storage account created"
    fi
}

# Create container
create_container() {
    log_info "Creating container: $CONTAINER_NAME"

    # Get storage account key
    STORAGE_KEY=$(az storage account keys list \
        --resource-group "$RESOURCE_GROUP" \
        --account-name "$STORAGE_ACCOUNT_NAME" \
        --query '[0].value' -o tsv)

    # Create container
    az storage container create \
        --name "$CONTAINER_NAME" \
        --account-name "$STORAGE_ACCOUNT_NAME" \
        --account-key "$STORAGE_KEY" \
        --public-access off \
        --output table
    log_success "Container created"
}

# Enable CORS for TypingMind
enable_cors() {
    log_info "Enabling CORS for TypingMind access..."

    # Get search service admin key
    ADMIN_KEY=$(az search admin-key show \
        --resource-group "$RESOURCE_GROUP" \
        --service-name "$SEARCH_SERVICE_NAME" \
        --query 'primaryKey' -o tsv)

    # Enable CORS using REST API
    SEARCH_ENDPOINT="https://$SEARCH_SERVICE_NAME.search.windows.net"

    curl -X POST \
        -H "Content-Type: application/json" \
        -H "api-key: $ADMIN_KEY" \
        -d '{"corsOptions": {"allowedOrigins": ["*"], "maxAgeInSeconds": 300}}' \
        "$SEARCH_ENDPOINT/cors?api-version=2023-11-01" \
        --silent --show-error || log_warning "CORS configuration may need manual setup"

    log_success "CORS enabled"
}

# Generate configuration file
generate_config() {
    log_info "Generating configuration file..."

    # Get required values
    ADMIN_KEY=$(az search admin-key show \
        --resource-group "$RESOURCE_GROUP" \
        --service-name "$SEARCH_SERVICE_NAME" \
        --query 'primaryKey' -o tsv)

    STORAGE_KEY=$(az storage account keys list \
        --resource-group "$RESOURCE_GROUP" \
        --account-name "$STORAGE_ACCOUNT_NAME" \
        --query '[0].value' -o tsv)

    STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
        --name "$STORAGE_ACCOUNT_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query 'connectionString' -o tsv)

    # Create .env file
    cat > .env << EOF
# Azure AI Search Configuration
AZURE_SEARCH_SERVICE_NAME=$SEARCH_SERVICE_NAME
AZURE_SEARCH_ADMIN_KEY=$ADMIN_KEY
AZURE_SEARCH_ENDPOINT=https://$SEARCH_SERVICE_NAME.search.windows.net
AZURE_SEARCH_INDEX_NAME=$INDEX_NAME

# Azure Storage Configuration
AZURE_STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT_NAME
AZURE_STORAGE_ACCOUNT_KEY=$STORAGE_KEY
AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION_STRING
AZURE_STORAGE_CONTAINER_NAME=$CONTAINER_NAME

# Resource Group
AZURE_RESOURCE_GROUP=$RESOURCE_GROUP
AZURE_LOCATION=$LOCATION
EOF

    log_success "Configuration saved to .env file"
}

# Display summary
show_summary() {
    log_success "Azure infrastructure setup complete!"
    echo ""
    echo "📋 Configuration Summary:"
    echo "  Resource Group: $RESOURCE_GROUP"
    echo "  AI Search Service: $SEARCH_SERVICE_NAME"
    echo "  Storage Account: $STORAGE_ACCOUNT_NAME"
    echo "  Container: $CONTAINER_NAME"
    echo "  Index: $INDEX_NAME"
    echo ""
    echo "🔧 Next Steps:"
    echo "  1. Run: python3 upload-training-data.py"
    echo "  2. Run: python3 configure-indexer.py"
    echo "  3. Run: python3 generate-typingmind-config.py"
    echo ""
    echo "📁 Configuration saved to: .env"
    echo "🔑 Admin key and storage key are in .env file"
}

# Main execution
main() {
    echo "🚀 Azure AI Search RAG Setup"
    echo "=============================="
    echo ""

    check_prerequisites
    create_resource_group
    create_search_service
    create_storage_account
    create_container
    enable_cors
    generate_config
    show_summary
}

# Run main function
main "$@"
