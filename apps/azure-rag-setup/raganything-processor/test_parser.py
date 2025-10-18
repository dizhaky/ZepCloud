#!/usr/bin/env python3
"""
Test RAG-Anything parsers with sample documents
Validates MinerU and Docling functionality before full integration
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_raganything_import():
    """Test if RAG-Anything is properly installed"""
    print("🔍 Testing RAG-Anything Installation...")
    try:
        from raganything import RAGAnything
        print("✅ RAG-Anything imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import RAG-Anything: {e}")
        print("   Run: pip install raganything[all]")
        return False

async def test_mineru_parser(test_file: str = None):
    """Test MinerU parser"""
    print("\n🔍 Testing MinerU Parser...")

    try:
        from raganything import RAGAnything

        if not test_file or not os.path.exists(test_file):
            print("⚠️  No test file provided, skipping actual parsing test")
            print("   Provide a PDF file path to test parsing")
            return True

        print(f"   Processing: {test_file}")

        rag = RAGAnything(
            parser="mineru",
            parse_method="auto",
            api_key=os.getenv("OPENAI_API_KEY")
        )

        output_dir = "./test_output/mineru"
        os.makedirs(output_dir, exist_ok=True)

        result = await rag.process_document_complete(
            file_path=test_file,
            output_dir=output_dir,
            parse_method="auto",
            display_stats=True
        )

        print(f"✅ MinerU parsing completed")
        print(f"   Output directory: {output_dir}")

        # Display extracted content summary
        if "tables" in result:
            print(f"   Tables extracted: {len(result['tables'])}")
        if "equations" in result:
            print(f"   Equations extracted: {len(result['equations'])}")
        if "images" in result:
            print(f"   Images processed: {len(result['images'])}")

        return True

    except Exception as e:
        print(f"❌ MinerU test failed: {e}")
        return False

async def test_docling_parser(test_file: str = None):
    """Test Docling parser"""
    print("\n🔍 Testing Docling Parser...")

    try:
        from raganything import RAGAnything

        if not test_file or not os.path.exists(test_file):
            print("⚠️  No test file provided, skipping actual parsing test")
            print("   Provide a DOCX file path to test parsing")
            return True

        print(f"   Processing: {test_file}")

        rag = RAGAnything(
            parser="docling",
            parse_method="auto",
            api_key=os.getenv("OPENAI_API_KEY")
        )

        output_dir = "./test_output/docling"
        os.makedirs(output_dir, exist_ok=True)

        result = await rag.process_document_complete(
            file_path=test_file,
            output_dir=output_dir,
            parse_method="auto",
            display_stats=True
        )

        print(f"✅ Docling parsing completed")
        print(f"   Output directory: {output_dir}")

        return True

    except Exception as e:
        print(f"❌ Docling test failed: {e}")
        return False

async def check_libreoffice():
    """Check if LibreOffice is installed (required for Office docs)"""
    print("\n🔍 Checking LibreOffice Installation...")

    import subprocess

    try:
        result = subprocess.run(
            ["libreoffice", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ LibreOffice installed: {version}")
            return True
        else:
            print("❌ LibreOffice not found")
            print("   Install: brew install --cask libreoffice (macOS)")
            return False

    except FileNotFoundError:
        print("❌ LibreOffice not found")
        print("   Install: brew install --cask libreoffice (macOS)")
        return False
    except Exception as e:
        print(f"⚠️  Could not check LibreOffice: {e}")
        return False

async def main():
    """Run all tests"""
    print("="*60)
    print("RAG-Anything Parser Testing Suite")
    print("="*60)

    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: OPENAI_API_KEY not set in .env")
        print("   Full parsing tests will be skipped")
    else:
        print(f"\n✅ OpenAI API Key: {api_key[:20]}...")

    # Test imports
    import_ok = await test_raganything_import()
    if not import_ok:
        print("\n❌ Installation test failed. Fix imports before continuing.")
        return 1

    # Check LibreOffice
    await check_libreoffice()

    # Get test files from command line if provided
    pdf_file = sys.argv[1] if len(sys.argv) > 1 else None
    docx_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not pdf_file and not docx_file:
        print("\n💡 To test parsing with actual files, run:")
        print("   python test_parser.py path/to/document.pdf path/to/document.docx")

    # Test parsers
    await test_mineru_parser(pdf_file)
    await test_docling_parser(docx_file)

    print("\n" + "="*60)
    print("✅ Testing Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. If tests passed, RAG-Anything is ready to use")
    print("2. Test with actual M365 documents from SharePoint")
    print("3. Proceed to building the preprocessing pipeline")

    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))

