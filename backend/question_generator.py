"""
Question Generator - RAG-based viva question generation
"""
from typing import List, Dict, Any
from dataclasses import dataclass

from backend.vector_store import get_vector_store
from backend.llm_engine import get_llm_engine
from backend.prompts import QUESTION_GENERATION_PROMPT, SINGLE_QUESTION_PROMPT


@dataclass
class VivaQuestion:
    """Represents a generated viva question"""
    question_number: int
    question_text: str
    expected_concepts: List[str]
    context_used: str
    difficulty: str  # easy, medium, hard


class QuestionGenerator:
    """
    RAG-based question generator for viva examination
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.vector_store = get_vector_store(session_id)
        self.llm_engine = get_llm_engine()
        
        # Store generated questions for the session
        self.questions: List[VivaQuestion] = []
        self.current_question_index = 0
    
    def generate_questions(self, num_questions: int = 5) -> List[VivaQuestion]:
        """
        Generate viva-style questions from the uploaded document
        
        Args:
            num_questions: Number of questions to generate
            
        Returns:
            List of VivaQuestion objects
        """
        print(f"📝 Generating {num_questions} questions for session: {self.session_id}")
        
        # Get comprehensive context for question generation
        query_topics = [
            "main methodology approach technique",
            "results findings conclusions",
            "problem statement objective motivation",
            "experiments evaluation metrics",
            "architecture design implementation"
        ]
        
        all_context = []
        for query in query_topics:
            results = self.vector_store.search(query, top_k=3)
            for chunk, score in results:
                if chunk.content not in all_context:
                    all_context.append(chunk.content)
        
        combined_context = "\n\n---\n\n".join(all_context[:10])
        
        # DEBUG: Check if context is empty
        print(f"📊 Context retrieved: {len(all_context)} chunks, {len(combined_context)} chars")
        
        # If no context, return informative fallback
        if not combined_context or len(combined_context) < 50:
            print("⚠️ WARNING: No PDF content found! Vector store may be empty.")
            print(f"   Vector store path: {self.vector_store.store_dir}")
            print(f"   Vector store exists: {self.vector_store.exists()}")
            
            # Return fallback questions that explain the issue
            return [VivaQuestion(
                question_number=1,
                question_text="No study material was found for this exam. Please ask your teacher to re-upload the PDF material.",
                expected_concepts=["System Notice"],
                context_used="No context available - PDF not processed",
                difficulty="N/A"
            )]
        
        # Generate questions using LLM
        prompt = QUESTION_GENERATION_PROMPT.format(
             context=combined_context,
             num_questions=num_questions
        )
        
        print(f"🤖 Sending to LLM ({self.llm_engine.model_name})...")
        
        response = self.llm_engine.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1500
        )
        
        print(f"📥 LLM Response received: {len(response)} chars")
        
        # Parse questions from response
        self.questions = self._parse_questions(response, combined_context)
        self.current_question_index = 0
        
        print(f"✅ Generated {len(self.questions)} viva questions")
        
        return self.questions
    
    def _parse_questions(
        self, 
        response: str, 
        context: str
    ) -> List[VivaQuestion]:
        """Parse questions from LLM response"""
        questions = []
        lines = response.strip().split('\n')
        
        question_number = 0
        for line in lines:
            line = line.strip()
            
            # Match numbered questions (1., 2., etc.)
            if line and (line[0].isdigit() or line.startswith('-')):
                # Clean the question text
                question_text = line.lstrip('0123456789.-) ').strip()
                
                if question_text and len(question_text) > 10:  # Valid question
                    question_number += 1
                    
                    # Extract expected concepts (keywords from question)
                    expected_concepts = self._extract_concepts(question_text, context)
                    
                    # Determine difficulty based on question type
                    difficulty = self._determine_difficulty(question_text)
                    
                    questions.append(VivaQuestion(
                        question_number=question_number,
                        question_text=question_text,
                        expected_concepts=expected_concepts,
                        context_used=context[:500] + "...",  # Truncate for storage
                        difficulty=difficulty
                    ))
        
        return questions
    
    def _extract_concepts(self, question: str, context: str) -> List[str]:
        """Extract expected concepts from question and context"""
        from backend.pdf_processor import PDFProcessor
        processor = PDFProcessor()
        
        # Get keywords from question
        question_keywords = processor.extract_key_terms(question)
        
        # Also get related keywords from context
        context_keywords = processor.extract_key_terms(context)
        
        # Combine and prioritize question keywords
        all_concepts = question_keywords[:5] + [
            k for k in context_keywords[:10] 
            if k not in question_keywords
        ]
        
        return all_concepts[:10]
    
    def _determine_difficulty(self, question: str) -> str:
        """Determine question difficulty based on question type"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['what if', 'hypothetically', 'could you propose']):
            return 'hard'
        elif any(word in question_lower for word in ['why', 'how does', 'explain the reasoning']):
            return 'medium'
        else:
            return 'easy'
    
    def get_next_question(self) -> VivaQuestion:
        """Get the next question in sequence"""
        if not self.questions:
            raise ValueError("No questions generated. Call generate_questions first.")
        
        if self.current_question_index >= len(self.questions):
            raise ValueError("All questions have been asked.")
        
        question = self.questions[self.current_question_index]
        self.current_question_index += 1
        
        return question
    
    def get_current_question(self) -> VivaQuestion:
        """Get current question without advancing"""
        if not self.questions:
            raise ValueError("No questions generated.")
        
        idx = max(0, self.current_question_index - 1)
        return self.questions[idx]
    
    def reset(self):
        """Reset question generator for new session"""
        self.questions = []
        self.current_question_index = 0
    
    def get_all_questions(self) -> List[VivaQuestion]:
        """Get all generated questions"""
        return self.questions
    
    def generate_single_question(self, topic_hint: str = None) -> VivaQuestion:
        """
        Generate a single targeted question
        
        Args:
            topic_hint: Optional topic to focus the question on
            
        Returns:
            Single VivaQuestion
        """
        query = topic_hint or "main concepts methodology findings"
        context = self.vector_store.get_context(query, top_k=5)
        
        prompt = SINGLE_QUESTION_PROMPT.format(context=context)
        
        response = self.llm_engine.generate(prompt, temperature=0.8)
        
        # Parse single question
        lines = response.strip().split('\n')
        question_text = ""
        expected_concepts = []
        
        for line in lines:
            if line.lower().startswith('question:'):
                question_text = line.replace('Question:', '').replace('question:', '').strip()
            elif line.lower().startswith('expected concepts:') or line.lower().startswith('expected:'):
                concepts_str = line.split(':', 1)[1].strip()
                expected_concepts = [c.strip() for c in concepts_str.split(',')]
        
        if not question_text:
            question_text = lines[0] if lines else "Unable to generate question"
        
        new_question = VivaQuestion(
            question_number=len(self.questions) + 1,
            question_text=question_text,
            expected_concepts=expected_concepts or self._extract_concepts(question_text, context),
            context_used=context[:500] + "...",
            difficulty=self._determine_difficulty(question_text)
        )
        
        self.questions.append(new_question)
        
        return new_question


def get_question_generator(session_id: str) -> QuestionGenerator:
    """Get question generator for a session"""
    return QuestionGenerator(session_id)
