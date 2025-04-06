#!/bin/bash
# Comprehensive E2E test script for the Financial Tracking API

# Set the base URL
BASE_URL="http://localhost:8000/api/v1"
# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_header() {
    echo -e "\n${BLUE}==== $1 ====${NC}"
}

# 1. Register a new user
print_header "REGISTERING A NEW USER"
REGISTER_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"username":"testuser2", "password":"password123"}' \
    $BASE_URL/auth/register)

if [[ "$REGISTER_RESPONSE" == "true" ]]; then
    print_success "User registration successful"
else
    print_error "User registration failed: $REGISTER_RESPONSE"
    exit 1
fi

# 2. Login to get a token
print_header "LOGGING IN"
TOKEN_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=testuser&password=password123" \
    $BASE_URL/auth/token)

# Extract token using grep and cut
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    print_error "Failed to get access token: $TOKEN_RESPONSE"
    exit 1
else
    print_success "Successfully obtained access token"
fi

# 3. Get user profile
print_header "GETTING USER PROFILE"
USER_PROFILE=$(curl -s -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    $BASE_URL/users/me)

USER_ID=$(echo $USER_PROFILE | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -z "$USER_ID" ]; then
    print_error "Failed to get user profile: $USER_PROFILE"
    exit 1
else
    print_success "Successfully got user profile with ID: $USER_ID"
fi

# 4. Get user balance
print_header "GETTING USER BALANCE"
BALANCE_RESPONSE=$(curl -s -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    $BASE_URL/users/balance)

BALANCE=$(echo $BALANCE_RESPONSE | grep -o '"balance":[0-9.]*' | cut -d':' -f2)

if [ -z "$BALANCE" ]; then
    print_error "Failed to get user balance: $BALANCE_RESPONSE"
    exit 1
else
    print_success "User balance: $BALANCE"
fi

# 5. Create a transaction - income
print_header "CREATING AN INCOME TRANSACTION"
INCOME_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -d '{"description":"Salary", "currency":"USD", "amount":1000, "is_income":true, "tags":["work", "monthly"]}' \
    $BASE_URL/transactions/)

if [[ "$INCOME_RESPONSE" == "true" ]]; then
    print_success "Income transaction created successfully"
else
    print_error "Failed to create income transaction: $INCOME_RESPONSE"
    exit 1
fi

# 6. Create a transaction - expense
print_header "CREATING AN EXPENSE TRANSACTION"
EXPENSE_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -d '{"description":"Groceries", "currency":"USD", "amount":50, "is_income":false, "tags":["food", "essential"]}' \
    $BASE_URL/transactions/)

if [[ "$EXPENSE_RESPONSE" == "true" ]]; then
    print_success "Expense transaction created successfully"
else
    print_error "Failed to create expense transaction: $EXPENSE_RESPONSE"
    exit 1
fi

# 7. Get recent transactions
print_header "GETTING RECENT TRANSACTIONS"
RECENT_RESPONSE=$(curl -s -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    $BASE_URL/transactions/recent)

# Verify we get an array of transactions
TRANSACTION_COUNT=$(echo $RECENT_RESPONSE | grep -o '"id"' | wc -l)

if [ "$TRANSACTION_COUNT" -gt 0 ]; then
    print_success "Got $TRANSACTION_COUNT recent transactions"
else
    print_error "Failed to get recent transactions: $RECENT_RESPONSE"
    exit 1
fi

# 8. Get all transactions
print_header "GETTING ALL TRANSACTIONS"
ALL_RESPONSE=$(curl -s -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    "$BASE_URL/transactions/?page=1&per_page=10")

# Extract the first transaction ID
FIRST_TRANSACTION_ID=$(echo $ALL_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$FIRST_TRANSACTION_ID" ]; then
    print_error "Failed to get transactions: $ALL_RESPONSE"
    exit 1
else
    print_success "Got transactions, first transaction ID: $FIRST_TRANSACTION_ID"
fi

# 9. Get a single transaction
print_header "GETTING A SINGLE TRANSACTION"
SINGLE_RESPONSE=$(curl -s -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    $BASE_URL/transactions/$FIRST_TRANSACTION_ID)

TRANSACTION_DESC=$(echo $SINGLE_RESPONSE | grep -o '"description":"[^"]*' | cut -d'"' -f4)

if [ -z "$TRANSACTION_DESC" ]; then
    print_error "Failed to get single transaction: $SINGLE_RESPONSE"
    exit 1
else
    print_success "Got transaction with description: $TRANSACTION_DESC"
fi

# 10. Get filtered transactions (by description)
print_header "GETTING FILTERED TRANSACTIONS BY DESCRIPTION"
FILTERED_RESPONSE=$(curl -s -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    "$BASE_URL/transactions/?description=Gro")

FILTERED_COUNT=$(echo $FILTERED_RESPONSE | grep -o '"id"' | wc -l)

if [ "$FILTERED_COUNT" -gt 0 ]; then
    print_success "Got $FILTERED_COUNT filtered transactions by description"
else
    print_error "Failed to get filtered transactions by description: $FILTERED_RESPONSE"
    exit 1
fi

# 11. Get filtered transactions (by tags)
print_header "GETTING FILTERED TRANSACTIONS BY TAGS"
TAGGED_RESPONSE=$(curl -s -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    "$BASE_URL/transactions/?tags=food")

TAGGED_COUNT=$(echo $TAGGED_RESPONSE | grep -o '"id"' | wc -l)

if [ "$TAGGED_COUNT" -gt 0 ]; then
    print_success "Got $TAGGED_COUNT filtered transactions by tags"
else
    print_error "Failed to get filtered transactions by tags: $TAGGED_RESPONSE"
    exit 1
fi

# 12. Delete a transaction
print_header "DELETING A TRANSACTION"
DELETE_RESPONSE=$(curl -s -X DELETE \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    $BASE_URL/transactions/$FIRST_TRANSACTION_ID)

if [[ "$DELETE_RESPONSE" == "true" ]]; then
    print_success "Transaction deleted successfully"
else
    print_error "Failed to delete transaction: $DELETE_RESPONSE"
    exit 1
fi

# 13. Check that the transaction is gone
print_header "VERIFYING TRANSACTION DELETION"
VERIFY_RESPONSE=$(curl -s -X GET \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    $BASE_URL/transactions/$FIRST_TRANSACTION_ID)

if [[ "$VERIFY_RESPONSE" == "null" ]]; then
    print_success "Transaction deletion verified"
else
    print_error "Transaction was not deleted properly: $VERIFY_RESPONSE"
    exit 1
fi

print_header "E2E TESTS COMPLETED SUCCESSFULLY"
echo "All tests passed! The API is working correctly."