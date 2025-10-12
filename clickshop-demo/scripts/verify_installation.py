# Fixed Verification Script for ClickShop Dependencies

import sys

print(f"Python: {sys.version}\n")
print("Verifying installed packages...\n")

# Test all imports with proper error handling
packages_status = []

# Strands
try:
    import strands
    packages_status.append(("✅ Strands", "installed"))
except ImportError as e:
    packages_status.append(("❌ Strands", f"NOT INSTALLED"))

# Boto3
try:
    import boto3
    packages_status.append(("✅ Boto3", boto3.__version__))
except ImportError as e:
    packages_status.append(("❌ Boto3", f"NOT INSTALLED"))

# psycopg3
try:
    import psycopg
    packages_status.append(("✅ psycopg3", psycopg.__version__))
except ImportError as e:
    packages_status.append(("❌ psycopg3", f"NOT INSTALLED"))

# pgvector
try:
    import pgvector
    packages_status.append(("✅ pgvector", "installed"))
except ImportError as e:
    packages_status.append(("❌ pgvector", f"NOT INSTALLED"))

# numpy
try:
    import numpy
    packages_status.append(("✅ numpy", numpy.__version__))
except ImportError as e:
    packages_status.append(("❌ numpy", f"NOT INSTALLED"))

# sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    packages_status.append(("✅ sentence-transformers", "installed"))
except ImportError as e:
    packages_status.append(("❌ sentence-transformers", f"NOT INSTALLED"))

# rich
try:
    from rich.console import Console
    packages_status.append(("✅ rich", "installed"))
except ImportError as e:
    packages_status.append(("❌ rich", f"NOT INSTALLED"))

# python-dotenv
try:
    from dotenv import load_dotenv
    packages_status.append(("✅ python-dotenv", "installed"))
except ImportError as e:
    packages_status.append(("❌ python-dotenv", f"NOT INSTALLED"))

# pydantic
try:
    import pydantic
    packages_status.append(("✅ pydantic", pydantic.__version__))
except ImportError as e:
    packages_status.append(("❌ pydantic", f"NOT INSTALLED"))

# sqlalchemy
try:
    import sqlalchemy
    packages_status.append(("✅ sqlalchemy", sqlalchemy.__version__))
except ImportError as e:
    packages_status.append(("❌ sqlalchemy", f"NOT INSTALLED"))

# Print results
print("=" * 70)
for package, version in packages_status:
    print(f"{package:.<50} {version}")
print("=" * 70)

# Check if all critical packages are installed
failed = [status for status in packages_status if "❌" in status[0]]

if not failed:
    print("\n🎉 All dependencies installed successfully!")
    print("\n✅ You're ready to proceed with:")
    print("   1. Aurora connection test")
    print("   2. Database schema initialization")
    print("   3. Running demos")
else:
    print("\n⚠️  Some dependencies are missing!")
    print("\nMissing packages:")
    for package, error in failed:
        print(f"  • {package.replace('❌ ', '')}")
    print("\n💡 Run: pip install -r requirements.txt")

print("\n" + "=" * 70)
