"""
Evaluation Engine - Hybrid keyword + semantic answer evaluation
"""
from typing import Dict, Any, List, Tuple
import re
import numpy as np
from dataclasses import dataclass

from backend.config import settings
from backend.embeddings import get_embedding_engine
from backend.vector_store import get_vector_store
from backend.llm_engine import get_llm_engine
from backend.prompts import ANSWER_EVALUATION_PROMPT
from backend.pdf_processor import PDFProcessor


@dataclass
class EvaluationResult:
    """Stores the result of answer evaluation"""
    question: str
    student_answer: str
    semantic_score: float
    keyword_score: float
    final_score: float
    llm_evaluation: str
    missing_concepts: List[str]
    feedback: str
    expected_keywords: List[str]
    matched_keywords: List[str]
    context_used: str


class EvaluationEngine:
    """
    Hybrid evaluation engine combining semantic similarity and keyword matching
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.embedding_engine = get_embedding_engine()
        self.vector_store = get_vector_store(session_id)
        self.llm_engine = get_llm_engine()
        self.pdf_processor = PDFProcessor()
        
        # Weights for hybrid scoring
        self.semantic_weight = settings.semantic_weight
        self.keyword_weight = settings.keyword_weight
    
    def evaluate_answer(
        self,
        question: str,
        student_answer: str,
        expected_answer: str = None
    ) -> EvaluationResult:
        """
        Evaluate a student's answer using hybrid scoring
        
        Args:
            question: The viva question
            student_answer: Student's response
            expected_answer: Optional expected answer (if not provided, uses context)
            
        Returns:
            EvaluationResult with detailed scoring
        """
        # Step 1: Retrieve relevant context
        context = self.vector_store.get_context(question, top_k=5)
        
        # Step 2: Extract keywords from context
        expected_keywords = self._extract_keywords(context, question)
        
        # Step 3: Calculate semantic similarity
        semantic_score = self._calculate_semantic_similarity(
            student_answer, 
            context
        )
        
        # Step 4: Calculate keyword coverage
        keyword_score, matched_keywords = self._calculate_keyword_coverage(
            student_answer, 
            expected_keywords
        )
        
        # Step 5: Calculate hybrid score
        hybrid_score = (
            self.semantic_weight * semantic_score + 
            self.keyword_weight * keyword_score
        )
        
        # Step 6: Get LLM evaluation for detailed feedback
        llm_result = self._get_llm_evaluation(
            question=question,
            student_answer=student_answer,
            context=context,
            expected_keywords=expected_keywords
        )
        
        # Step 7: Combine scores (weight LLM opinion with hybrid score)
        llm_score = llm_result.get("score", hybrid_score * 10) / 10  # Normalize to 0-1
        final_score = (0.6 * hybrid_score + 0.4 * llm_score) * 10  # Scale to 1-10
        final_score = max(1, min(10, round(final_score)))  # Clamp between 1-10
        
        return EvaluationResult(
            question=question,
            student_answer=student_answer,
            semantic_score=round(semantic_score * 10, 2),
            keyword_score=round(keyword_score * 10, 2),
            final_score=final_score,
            llm_evaluation=llm_result.get("evaluation", ""),
            missing_concepts=llm_result.get("missing_concepts", []),
            feedback=llm_result.get("feedback", ""),
            expected_keywords=expected_keywords,
            matched_keywords=matched_keywords,
            context_used=context
        )
    
    def _extract_keywords(self, context: str, question: str) -> List[str]:
        """Extract important keywords from context and question"""
        combined_text = f"{context}\n{question}"
        
        # Use PDF processor's keyword extraction
        all_keywords = self.pdf_processor.extract_key_terms(combined_text)
        
        # Filter to most relevant (top 20)
        return all_keywords[:20]
    
    def _calculate_semantic_similarity(
        self, 
        student_answer: str, 
        context: str
    ) -> float:
        """
        Calculate semantic similarity between answer and context
        
        Returns:
            Similarity score (0 to 1)
        """
        if not student_answer.strip():
            return 0.0
        
        # Get embeddings
        answer_embedding = self.embedding_engine.embed_text(student_answer)
        context_embedding = self.embedding_engine.embed_text(context)
        
        # Calculate cosine similarity
        similarity = self.embedding_engine.compute_similarity(
            answer_embedding, 
            context_embedding
        )
        
        # Normalize to 0-1 range (cosine similarity can be negative)
        return max(0, min(1, (similarity + 1) / 2))
    
    def _calculate_keyword_coverage(
        self, 
        student_answer: str, 
        expected_keywords: List[str]
    ) -> Tuple[float, List[str]]:
        """
        Calculate keyword coverage in student's answer
        
        Returns:
            Tuple of (coverage_score, matched_keywords)
        """
        if not expected_keywords:
            return 0.5, []  # Neutral score if no keywords
        
        # Normalize answer for matching
        answer_lower = student_answer.lower()
        answer_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', answer_lower))
        
        matched = []
        for keyword in expected_keywords:
            keyword_lower = keyword.lower()
            # Check for exact match or partial match
            if keyword_lower in answer_lower or keyword_lower in answer_words:
                matched.append(keyword)
            # Also check for stemmed/partial matches
            elif any(keyword_lower in word or word in keyword_lower 
                    for word in answer_words if len(word) > 4):
                matched.append(keyword)
        
        coverage = len(matched) / len(expected_keywords) if expected_keywords else 0
        
        return coverage, matched
    
    def _get_llm_evaluation(
        self,
        question: str,
        student_answer: str,
        context: str,
        expected_keywords: List[str]
    ) -> Dict[str, Any]:
        """Get detailed evaluation from LLM"""
        prompt = ANSWER_EVALUATION_PROMPT.format(
            context=context,
            question=question,
            expected_keywords=", ".join(expected_keywords),
            student_answer=student_answer
        )
        
        try:
            result = self.llm_engine.generate_json(prompt, temperature=0.3)
            
            # Validate and clean result
            if "score" in result:
                result["score"] = max(1, min(10, int(result["score"])))
            
            return result
            
        except Exception as e:
            print(f"⚠️ LLM evaluation error: {e}")
            return {
                "evaluation": "Unable to generate detailed evaluation",
                "missing_concepts": [],
                "score": 5,
                "feedback": "Evaluation based on keyword and semantic matching only"
            }
    
    def format_result(self, result: EvaluationResult) -> str:
        """Format evaluation result for display"""
        return f"""
═══════════════════════════════════════════════════════════════
📋 EVALUATION REPORT
═══════════════════════════════════════════════════════════════

❓ **Question:**
{result.question}

📝 **Student Answer:**
{result.student_answer}

═══════════════════════════════════════════════════════════════
📊 SCORING BREAKDOWN
═══════════════════════════════════════════════════════════════

🧠 Semantic Similarity Score: {result.semantic_score}/10
🔑 Keyword Coverage Score: {result.keyword_score}/10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ **FINAL SCORE: {result.final_score}/10**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **Matched Keywords ({len(result.matched_keywords)}):**
{', '.join(result.matched_keywords) or 'None'}

❌ **Missing Concepts:**
{', '.join(result.missing_concepts) or 'None identified'}

═══════════════════════════════════════════════════════════════
📜 DETAILED EVALUATION
═══════════════════════════════════════════════════════════════
{result.llm_evaluation}

💬 **Feedback:**
{result.feedback}
═══════════════════════════════════════════════════════════════
"""


def get_evaluation_engine(session_id: str) -> EvaluationEngine:
    """Get evaluation engine for a session"""
    return EvaluationEngine(session_id)


def evaluate_answer(question_obj, answer_text, context, session_id: str = None) -> Dict[str, Any]:
    """
    Standalone wrapper for evaluation to be used by frontend
    
    Args:
        question_obj: The question object or text
        answer_text: Student's answer
        context: PDF context (passed from frontend)
        session_id: Exam ID for correct vector store lookup
    """
    # Use provided session_id or fallback
    sid = session_id or "global_session"
    engine = get_evaluation_engine(sid)
    
    # Extract text if question is an object
    q_text = question_obj.question_text if hasattr(question_obj, 'question_text') else str(question_obj)
    
    print(f"🔍 Evaluating answer for session: {sid}")
    print(f"   Question: {q_text[:50]}...")
    print(f"   Answer: {answer_text[:50]}...")
    
    # Perform evaluation
    result = engine.evaluate_answer(
        question=q_text,
        student_answer=answer_text
    )
    
    print(f"✅ Evaluation complete. Score: {result.final_score}/10")
    
    # Return dict format expected by frontend
    return {
        "evaluation": result.llm_evaluation,
        "score": result.final_score,
        "feedback": result.feedback,
        "missing_concepts": result.missing_concepts
    }
