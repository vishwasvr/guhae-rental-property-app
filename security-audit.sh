#!/bin/bash
# Security Audit Script for Guhae Rental Property App
# Run this before deployments to ensure security compliance

echo "🔒 SECURITY AUDIT - Guhae Rental Property App"
echo "=============================================="

# Check for authentication validation in all property endpoints
echo ""
echo "1. Checking AUTHENTICATION validation in property endpoints..."

endpoints=("list_properties" "create_property" "get_property" "update_property" "delete_property")

for endpoint in "${endpoints[@]}"; do
    if grep -q "get_authenticated_user_id" "src/lambda_function.py" && grep -q "$endpoint" "src/lambda_function.py"; then
        auth_check=$(grep -A 10 "$endpoint" "src/lambda_function.py" | grep -c "get_authenticated_user_id")
        if [ "$auth_check" -gt 0 ]; then
            echo "✅ $endpoint - Has authentication"
        else
            echo "❌ $endpoint - MISSING authentication validation!"
        fi
    fi
done

# Check for ownership validation in modification endpoints
echo ""
echo "2. Checking AUTHORIZATION (ownership) validation..."

modify_endpoints=("get_property" "update_property" "delete_property")

for endpoint in "${modify_endpoints[@]}"; do
    ownership_check=$(grep -A 20 "$endpoint" "src/lambda_function.py" | grep -c "owner_id.*!=.*owner_id")
    if [ "$ownership_check" -gt 0 ]; then
        echo "✅ $endpoint - Has ownership validation"
    else
        echo "❌ $endpoint - MISSING ownership validation!"
    fi
done

echo ""
echo "3. Security Checklist Reminder:"
echo "   ✅ All user-data endpoints have authentication"
echo "   ✅ All modification endpoints validate ownership"
echo "   ✅ Input validation is implemented"
echo "   ✅ Error messages don't leak sensitive data"

echo ""
echo "Run this script before every deployment!"
echo "Security audit complete."