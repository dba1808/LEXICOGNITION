"""
PDF Processing Module - Handles PDF extraction and chunking
"""
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dataclasses import dataclass

from backend.config import settings


@dataclass
class PDFChunk:
    """Represents a chunk of text from a PDF"""
    content: str
    page_number: int
    chunk_index: int
    metadata: Dict[str, Any]


class PDFProcessor:
    """
    PDF Processor using pdfplumber for accurate extraction
    """
    
    def __init__(
        self, 
        chunk_size: int = None, 
        chunk_overlap: int = None
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract text from PDF with page-level metadata
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        full_text = ""
        pages_data = []
        
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text() or ""
                
                # Clean up the extracted text
                page_text = self._clean_text(page_text)
                
                pages_data.append({
                    "page_number": page_num,
                    "text": page_text,
                    "word_count": len(page_text.split())
                })
                
                full_text += f"\n[Page {page_num}]\n{page_text}\n"
        
        return {
            "full_text": full_text.strip(),
            "pages": pages_data,
            "total_pages": total_pages,
            "file_name": pdf_path.name
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might break processing
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        # Normalize newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    def chunk_text(
        self, 
        extracted_data: Dict[str, Any]
    ) -> List[PDFChunk]:
        """
        Split extracted text into chunks for embedding
        
        Args:
            extracted_data: Output from extract_text_from_pdf
            
        Returns:
            List of PDFChunk objects
        """
        chunks = []
        chunk_index = 0
        
        for page_data in extracted_data["pages"]:
            page_text = page_data["text"]
            page_number = page_data["page_number"]
            
            # Split page text into chunks
            page_chunks = self.text_splitter.split_text(page_text)
            
            for chunk_text in page_chunks:
                if chunk_text.strip():
                    chunks.append(PDFChunk(
                        content=chunk_text,
                        page_number=page_number,
                        chunk_index=chunk_index,
                        metadata={
                            "source": extracted_data["file_name"],
                            "page": page_number,
                            "chunk_id": chunk_index
                        }
                    ))
                    chunk_index += 1
        
        return chunks
    
    def process_pdf(self, pdf_path: Path) -> List[PDFChunk]:
        """
        Complete PDF processing pipeline
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of PDFChunk objects ready for embedding
        """
        extracted_data = self.extract_text_from_pdf(pdf_path)
        chunks = self.chunk_text(extracted_data)
        
        print(f"✅ Processed '{pdf_path.name}': {len(chunks)} chunks from {extracted_data['total_pages']} pages")
        
        return chunks
    
    def extract_key_terms(self, text: str) -> List[str]:
        """
        Extract key terms from text for keyword matching
        
        Args:
            text: Input text
            
        Returns:
            List of key terms
        """
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
            'it', 'its', 'this', 'that', 'these', 'those', 'i', 'we', 'you',
            'he', 'she', 'they', 'them', 'their', 'our', 'your', 'his', 'her'
        }
        
        # Tokenize and filter
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        key_terms = [w for w in words if w not in stop_words]
        
        # Get unique terms while preserving order
        seen = set()
        unique_terms = []
        for term in key_terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        return unique_terms


# Factory function
def get_pdf_processor() -> PDFProcessor:
    """Get PDF processor instance"""
    return PDFProcessor()
