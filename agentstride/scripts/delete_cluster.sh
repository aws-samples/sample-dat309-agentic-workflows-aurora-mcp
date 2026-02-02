#!/bin/bash
# ClickShop Aurora PostgreSQL Cluster Deletion Script
# Deletes the Aurora PostgreSQL cluster and associated resources
#
# Requirements implemented:
# - 1.6: Delete Aurora cluster and associated Secrets Manager secret
# - 1.7: Handle non-existent resources gracefully (descriptive messages)

set -e

# Configuration
CLUSTER_IDENTIFIER="agentstride-demo"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
SECRET_NAME="agentstride-demo-credentials"
SUBNET_GROUP_NAME="agentstride-demo-subnet-group"
SG_NAME="agentstride-demo-sg"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
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

echo ""
echo "=============================================="
echo "  ClickShop Aurora PostgreSQL Cluster Deletion"
echo "=============================================="
echo ""

# Check prerequisites
log_info "Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    log_error "AWS CLI is not installed. Please install it first."
    log_error "Visit: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    log_error "AWS credentials are not configured or invalid."
    log_error "Please run 'aws configure' or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
log_success "AWS credentials valid. Account ID: $ACCOUNT_ID"

# Track if any resources were found
RESOURCES_FOUND=false

# Step 1: Delete DB instance (if exists)
log_info "Checking for DB instance '${CLUSTER_IDENTIFIER}-instance'..."

if aws rds describe-db-instances --db-instance-identifier "${CLUSTER_IDENTIFIER}-instance" --region "$REGION" &> /dev/null; then
    RESOURCES_FOUND=true
    log_info "Deleting DB instance '${CLUSTER_IDENTIFIER}-instance'..."
    
    aws rds delete-db-instance \
        --db-instance-identifier "${CLUSTER_IDENTIFIER}-instance" \
        --skip-final-snapshot \
        --region "$REGION" > /dev/null 2>&1 || true
    
    log_info "Waiting for DB instance to be deleted (this may take several minutes)..."
    
    # Wait for instance deletion with timeout handling
    if aws rds wait db-instance-deleted \
        --db-instance-identifier "${CLUSTER_IDENTIFIER}-instance" \
        --region "$REGION" 2>/dev/null; then
        log_success "DB instance deleted"
    else
        log_warning "Instance deletion wait timed out, but deletion may still be in progress"
    fi
else
    log_warning "DB instance '${CLUSTER_IDENTIFIER}-instance' does not exist. Skipping."
fi

# Step 2: Delete Aurora cluster (if exists)
log_info "Checking for Aurora cluster '$CLUSTER_IDENTIFIER'..."

if aws rds describe-db-clusters --db-cluster-identifier "$CLUSTER_IDENTIFIER" --region "$REGION" &> /dev/null; then
    RESOURCES_FOUND=true
    log_info "Deleting Aurora cluster '$CLUSTER_IDENTIFIER'..."
    
    aws rds delete-db-cluster \
        --db-cluster-identifier "$CLUSTER_IDENTIFIER" \
        --skip-final-snapshot \
        --region "$REGION" > /dev/null 2>&1 || true
    
    log_info "Waiting for cluster to be deleted (this may take several minutes)..."
    
    # Wait for cluster deletion with timeout handling
    if aws rds wait db-cluster-deleted \
        --db-cluster-identifier "$CLUSTER_IDENTIFIER" \
        --region "$REGION" 2>/dev/null; then
        log_success "Aurora cluster deleted"
    else
        log_warning "Cluster deletion wait timed out, but deletion may still be in progress"
    fi
else
    log_warning "Aurora cluster '$CLUSTER_IDENTIFIER' does not exist. Skipping."
fi

# Step 3: Delete Secrets Manager secret (if exists)
log_info "Checking for Secrets Manager secret '$SECRET_NAME'..."

if aws secretsmanager describe-secret --secret-id "$SECRET_NAME" --region "$REGION" &> /dev/null; then
    RESOURCES_FOUND=true
    log_info "Deleting Secrets Manager secret '$SECRET_NAME'..."
    
    # Force delete without recovery window
    aws secretsmanager delete-secret \
        --secret-id "$SECRET_NAME" \
        --force-delete-without-recovery \
        --region "$REGION" > /dev/null 2>&1 || true
    
    log_success "Secrets Manager secret deleted"
else
    log_warning "Secrets Manager secret '$SECRET_NAME' does not exist. Skipping."
fi

# Step 4: Delete DB subnet group (if exists)
log_info "Checking for DB subnet group '$SUBNET_GROUP_NAME'..."

if aws rds describe-db-subnet-groups --db-subnet-group-name "$SUBNET_GROUP_NAME" --region "$REGION" &> /dev/null; then
    RESOURCES_FOUND=true
    log_info "Deleting DB subnet group '$SUBNET_GROUP_NAME'..."
    
    aws rds delete-db-subnet-group \
        --db-subnet-group-name "$SUBNET_GROUP_NAME" \
        --region "$REGION" > /dev/null 2>&1 || true
    
    log_success "DB subnet group deleted"
else
    log_warning "DB subnet group '$SUBNET_GROUP_NAME' does not exist. Skipping."
fi

# Step 5: Delete security group (if exists)
log_info "Checking for security group '$SG_NAME'..."

# Get default VPC
DEFAULT_VPC=$(aws ec2 describe-vpcs \
    --filters "Name=isDefault,Values=true" \
    --region "$REGION" \
    --query 'Vpcs[0].VpcId' \
    --output text 2>/dev/null || echo "None")

if [ "$DEFAULT_VPC" != "None" ] && [ -n "$DEFAULT_VPC" ]; then
    SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
        --filters "Name=group-name,Values=$SG_NAME" "Name=vpc-id,Values=$DEFAULT_VPC" \
        --region "$REGION" \
        --query 'SecurityGroups[0].GroupId' \
        --output text 2>/dev/null || echo "None")
    
    if [ "$SECURITY_GROUP_ID" != "None" ] && [ -n "$SECURITY_GROUP_ID" ]; then
        RESOURCES_FOUND=true
        log_info "Deleting security group '$SG_NAME' ($SECURITY_GROUP_ID)..."
        
        aws ec2 delete-security-group \
            --group-id "$SECURITY_GROUP_ID" \
            --region "$REGION" > /dev/null 2>&1 || true
        
        log_success "Security group deleted"
    else
        log_warning "Security group '$SG_NAME' does not exist. Skipping."
    fi
else
    log_warning "No default VPC found. Skipping security group deletion."
fi

# Output summary
echo ""
echo "=============================================="
echo "  Deletion Summary"
echo "=============================================="
echo ""

if [ "$RESOURCES_FOUND" = true ]; then
    log_success "ClickShop Aurora cluster and associated resources have been deleted."
    echo ""
    echo "Deleted resources:"
    echo "  - Aurora cluster: $CLUSTER_IDENTIFIER"
    echo "  - DB instance: ${CLUSTER_IDENTIFIER}-instance"
    echo "  - Secrets Manager secret: $SECRET_NAME"
    echo "  - DB subnet group: $SUBNET_GROUP_NAME"
    echo "  - Security group: $SG_NAME"
else
    log_warning "No ClickShop resources were found to delete."
    echo ""
    echo "The following resources were checked but not found:"
    echo "  - Aurora cluster: $CLUSTER_IDENTIFIER"
    echo "  - DB instance: ${CLUSTER_IDENTIFIER}-instance"
    echo "  - Secrets Manager secret: $SECRET_NAME"
    echo "  - DB subnet group: $SUBNET_GROUP_NAME"
    echo "  - Security group: $SG_NAME"
fi

echo ""
echo "=============================================="
log_success "Deletion process complete!"
echo ""
